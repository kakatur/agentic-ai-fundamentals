import pytest

from llmops import (
    classify_baseline,
    classify_candidate,
    evaluate_release,
    golden_examples,
    parse_prediction,
    recall_for_high_severity,
    run_eval,
)


def test_baseline_release_is_promoted():
    traces = run_eval(
        examples=golden_examples(),
        model=classify_baseline,
        model_version="support-router",
        prompt_version="triage-v1",
    )

    report = evaluate_release(traces=traces)

    assert report.accuracy == 1.0
    assert report.high_severity_recall == 1.0
    assert report.promoted is True
    assert {trace.prompt_version for trace in traces} == {"triage-v1"}


def test_candidate_regression_blocks_release():
    traces = run_eval(
        examples=golden_examples(),
        model=classify_candidate,
        model_version="support-router",
        prompt_version="triage-v2",
    )

    report = evaluate_release(traces=traces)

    assert report.promoted is False
    assert report.accuracy < 1.0
    assert report.high_severity_recall < 1.0
    assert any(
        check.name == "high_severity_recall" and not check.passed
        for check in report.risk_checks
    )


def test_trace_records_explain_the_failed_case():
    traces = run_eval(
        examples=golden_examples(),
        model=classify_candidate,
        model_version="support-router",
        prompt_version="triage-v2",
    )

    refund_trace = next(
        trace for trace in traces if trace.example_id == "billing-refund"
    )

    assert refund_trace.expected_intent == "billing"
    assert refund_trace.actual_intent == "billing"
    assert refund_trace.expected_severity == "high"
    assert refund_trace.actual_severity == "normal"
    assert refund_trace.passed is False
    assert refund_trace.trace_id


def test_high_severity_recall_focuses_on_critical_examples():
    traces = run_eval(
        examples=golden_examples(),
        model=classify_candidate,
        model_version="support-router",
        prompt_version="triage-v2",
    )

    assert recall_for_high_severity(traces) == 0.5


def test_parser_rejects_unknown_output_shape():
    with pytest.raises(ValueError, match="intent\\|severity\\|answer"):
        parse_prediction("billing high priority")


def test_parser_rejects_unknown_labels():
    with pytest.raises(ValueError, match="Unknown intent"):
        parse_prediction("sales|high|Route this.")
