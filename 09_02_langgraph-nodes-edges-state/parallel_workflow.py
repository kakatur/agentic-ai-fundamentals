"""Parallel LangGraph branches that safely merge updates with a reducer."""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class ResearchState(TypedDict):
    topic: str
    notes: Annotated[list[str], operator.add]
    summary: str


def research_reliability(state: ResearchState) -> dict:
    return {"notes": [f"Reliability constraints for {state['topic']}"]}


def research_operations(state: ResearchState) -> dict:
    return {"notes": [f"Operational constraints for {state['topic']}"]}


def synthesize(state: ResearchState) -> dict:
    ordered_notes = sorted(state["notes"])
    return {"summary": " | ".join(ordered_notes)}


def build_parallel_graph():
    """Fan out to two nodes, merge their updates, then join."""

    builder = StateGraph(ResearchState)
    builder.add_node("research_reliability", research_reliability)
    builder.add_node("research_operations", research_operations)
    builder.add_node("synthesize", synthesize)

    builder.add_edge(START, "research_reliability")
    builder.add_edge(START, "research_operations")
    builder.add_edge(
        ["research_reliability", "research_operations"],
        "synthesize",
    )
    builder.add_edge("synthesize", END)
    return builder.compile()
