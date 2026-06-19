from parallel_workflow import build_parallel_graph
from support_workflow import build_support_graph, initial_state


def test_low_risk_request_uses_fast_path():
    result = build_support_graph().invoke(
        initial_state("How do I reset my password?")
    )

    assert result["route"] == "fast_path"
    assert result["risk_score"] == 0
    assert result["response"].startswith("Automated answer")
    assert result["audit_log"] == [
        "normalized request",
        "risk assessed: 0",
        "fast path completed",
        "workflow finalized via fast_path",
    ]


def test_high_risk_request_uses_review_path():
    result = build_support_graph().invoke(
        initial_state("Please investigate this payment refund")
    )

    assert result["route"] == "review_path"
    assert result["risk_score"] == 8
    assert result["response"].startswith("Human review required")
    assert "review path selected" in result["audit_log"]


def test_nodes_return_partial_updates_without_erasing_other_channels():
    result = build_support_graph().invoke(initial_state("Account question"))

    assert result["request"] == "Account question"
    assert result["normalized_request"] == "account question"
    assert result["response"]


def test_stream_updates_exposes_node_boundaries():
    updates = list(
        build_support_graph().stream(
            initial_state("Security issue"),
            stream_mode="updates",
        )
    )

    assert [next(iter(update)) for update in updates] == [
        "normalize_request",
        "assess_risk",
        "review_path",
        "finalize",
    ]


def test_parallel_branches_merge_notes_before_join():
    result = build_parallel_graph().invoke(
        {
            "topic": "agent deployment",
            "notes": [],
            "summary": "",
        }
    )

    assert sorted(result["notes"]) == [
        "Operational constraints for agent deployment",
        "Reliability constraints for agent deployment",
    ]
    assert result["summary"] == (
        "Operational constraints for agent deployment"
        " | Reliability constraints for agent deployment"
    )
