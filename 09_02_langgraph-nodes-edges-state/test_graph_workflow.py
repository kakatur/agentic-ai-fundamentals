import pytest

from graph_workflow import (
    END,
    NodeResult,
    StateGraph,
    SupportState,
    build_support_graph,
    merge_state,
)


def test_billing_request_flows_through_normal_edges_to_finalize() -> None:
    run = build_support_graph().invoke(
        SupportState(request="Please refund this duplicate charge.")
    )

    assert run.visited == (
        "classify",
        "retrieve_policy",
        "draft_response",
        "review_risk",
        "finalize",
    )
    assert run.state.route == "billing"
    assert run.state.risk == 0
    assert "refunds require invoice id" in run.state.facts
    assert run.state.final_answer is not None
    assert "Facts used" in run.state.final_answer


def test_conditional_edge_routes_high_risk_request_to_escalation() -> None:
    run = build_support_graph().invoke(
        SupportState(
            request="Urgent legal issue from an enterprise customer.",
            customer_tier="enterprise",
        )
    )

    assert run.visited[-1] == "escalate"
    assert "finalize" not in run.visited
    assert run.state.route == "general"
    assert run.state.risk >= 2
    assert "Escalate to human review" in run.state.final_answer
    assert "human_review" in run.state.history


def test_tuple_fields_act_like_reducers_when_state_is_merged() -> None:
    state = SupportState(request="Need help", facts=("first fact",), history=("start",))
    merged = merge_state(
        state,
        NodeResult(facts=("second fact",), history=("custom event",)),
        node_name="node_a",
    )

    assert merged.facts == ("first fact", "second fact")
    assert merged.history == ("start", "node_a", "custom event")


def test_graph_requires_an_entry_point_before_compile() -> None:
    graph = StateGraph()
    graph.add_node("single", lambda state: NodeResult(final_answer="done"))

    with pytest.raises(ValueError, match="set_entry_point"):
        graph.compile()


def test_runtime_stops_infinite_graphs_with_max_steps() -> None:
    graph = StateGraph()
    graph.add_node("loop", lambda state: NodeResult(history=("tick",)))
    graph.set_entry_point("loop")
    graph.add_edge("loop", "loop")

    with pytest.raises(RuntimeError, match="did not reach END"):
        graph.compile().invoke(SupportState(request="loop"), max_steps=3)


def test_unknown_conditional_branch_fails_loudly() -> None:
    graph = StateGraph()
    graph.add_node("start", lambda state: NodeResult())
    graph.set_entry_point("start")
    graph.add_conditional_edges("start", lambda state: "missing", {"done": END})

    with pytest.raises(ValueError, match="unknown branch"):
        graph.compile().invoke(SupportState(request="branch"))
