import pytest

from context_budget import ContextItem, build_context, edge_load_context, reserve_response_budget


def test_reserve_response_budget_keeps_generation_space():
    assert reserve_response_budget(1000, response_tokens=200, safety_margin=50) == 750


def test_reserve_response_budget_rejects_impossible_budget():
    with pytest.raises(ValueError):
        reserve_response_budget(100, response_tokens=100, safety_margin=1)


def test_build_context_prefers_pinned_and_high_priority_items():
    items = [
        ContextItem("low", "low value " * 20, priority=1),
        ContextItem("critical", "must keep", priority=1, pinned=True),
        ContextItem("recent", "important", priority=4),
    ]
    report = build_context(items, max_tokens=20)
    assert [item.label for item in report.selected] == ["critical", "recent"]
    assert [item.label for item in report.dropped] == ["low"]


def test_edge_load_context_places_critical_facts_near_edges():
    selected = (
        ContextItem("policy", "Manager approval is required.", pinned=True),
        ContextItem("ticket", "The invoice is duplicated."),
    )
    prompt = edge_load_context("Follow policy.", selected, "Refund it?")
    assert prompt.index("Manager approval") < prompt.index("The invoice")
    assert prompt.rstrip().endswith("Refund it?")
