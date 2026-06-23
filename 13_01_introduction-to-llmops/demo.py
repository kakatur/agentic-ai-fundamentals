from llmops import (
    classify_baseline,
    classify_candidate,
    evaluate_release,
    golden_examples,
    run_eval,
)


def print_report(name: str, report) -> None:
    print(f"\n{name}")
    print("-" * len(name))
    print(f"accuracy: {report.accuracy:.0%}")
    print(f"high severity recall: {report.high_severity_recall:.0%}")
    print(f"average latency: {report.average_latency_ms:.2f}ms")
    print(f"average tokens: {report.average_tokens:.1f}")
    print(f"promoted: {report.promoted}")

    for check in report.risk_checks:
        status = "pass" if check.passed else "fail"
        print(f"{status}: {check.name} ({check.detail})")


def main() -> None:
    examples = golden_examples()

    baseline_traces = run_eval(
        examples=examples,
        model=classify_baseline,
        model_version="support-router-2026-06-23",
        prompt_version="triage-v1",
    )
    candidate_traces = run_eval(
        examples=examples,
        model=classify_candidate,
        model_version="support-router-2026-06-23",
        prompt_version="triage-v2",
    )

    print_report("baseline", evaluate_release(traces=baseline_traces))
    print_report("candidate", evaluate_release(traces=candidate_traces))

    failed = [trace for trace in candidate_traces if not trace.passed]
    if failed:
        print("\nfailed candidate traces")
        for trace in failed:
            print(
                f"{trace.example_id}: expected "
                f"{trace.expected_intent}/{trace.expected_severity}, got "
                f"{trace.actual_intent}/{trace.actual_severity}"
            )


if __name__ == "__main__":
    main()
