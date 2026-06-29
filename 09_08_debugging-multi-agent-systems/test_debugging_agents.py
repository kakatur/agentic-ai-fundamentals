from debugging_agents import TraceEvent, analyze_trace, sample_bad_trace


def test_detects_handoff_loop_and_missing_answer():
    findings = analyze_trace(sample_bad_trace())
    codes = {finding.code for finding in findings}
    assert "handoff_loop" in codes
    assert "missing_final_answer" in codes


def test_detects_state_regression():
    findings = analyze_trace(sample_bad_trace())
    assert any(finding.code == "state_regression" for finding in findings)


def test_clean_trace_has_no_findings():
    events = (
        TraceEvent(1, "coordinator", "handoff", "billing", 1),
        TraceEvent(2, "billing", "reply", None, 2),
        TraceEvent(3, "coordinator", "final_answer", None, 3),
    )
    assert analyze_trace(events) == []
