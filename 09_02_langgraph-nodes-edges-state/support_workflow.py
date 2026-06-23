"""A deterministic LangGraph workflow demonstrating state, nodes, and edges."""

from __future__ import annotations

import operator
import re
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class SupportState(TypedDict):
    """Shared state for the support-triage graph."""

    request: str
    normalized_request: str
    risk_score: int
    route: Literal["fast_path", "review_path"]
    response: str
    audit_log: Annotated[list[str], operator.add]


def normalize_request(state: SupportState) -> dict:
    """Normalize user input and emit only the channels this node changes."""

    normalized = " ".join(state["request"].lower().split())
    return {
        "normalized_request": normalized,
        "audit_log": ["normalized request"],
    }


def assess_risk(state: SupportState) -> dict:
    """Assign a simple, deterministic risk score for the routing example."""

    high_risk_terms = {"refund", "security", "breach", "payment", "legal"}
    request_terms = set(
        re.findall(r"\b[\w'-]+\b", state["normalized_request"])
    )
    matched_terms = high_risk_terms.intersection(request_terms)
    score = min(len(matched_terms) * 4, 10)
    route: Literal["fast_path", "review_path"] = (
        "review_path" if score >= 4 else "fast_path"
    )
    return {
        "risk_score": score,
        "route": route,
        "audit_log": [f"risk assessed: {score}"],
    }


def route_after_assessment(
    state: SupportState,
) -> Literal["fast_path", "review_path"]:
    """Choose the next node without mutating state."""

    return state["route"]


def fast_path(state: SupportState) -> dict:
    """Handle low-risk requests automatically."""

    return {
        "response": f"Automated answer for: {state['normalized_request']}",
        "audit_log": ["fast path completed"],
    }


def review_path(state: SupportState) -> dict:
    """Prepare high-risk requests for human review."""

    return {
        "response": f"Human review required for: {state['normalized_request']}",
        "audit_log": ["review path selected"],
    }


def finalize(state: SupportState) -> dict:
    """Record completion while preserving the response from the chosen branch."""

    return {"audit_log": [f"workflow finalized via {state['route']}"]}


def build_support_graph():
    """Build and compile the support workflow."""

    builder = StateGraph(SupportState)
    builder.add_node("normalize_request", normalize_request)
    builder.add_node("assess_risk", assess_risk)
    builder.add_node("fast_path", fast_path)
    builder.add_node("review_path", review_path)
    builder.add_node("finalize", finalize)

    builder.add_edge(START, "normalize_request")
    builder.add_edge("normalize_request", "assess_risk")
    builder.add_conditional_edges(
        "assess_risk",
        route_after_assessment,
        {
            "fast_path": "fast_path",
            "review_path": "review_path",
        },
    )
    builder.add_edge("fast_path", "finalize")
    builder.add_edge("review_path", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile()


def initial_state(request: str) -> SupportState:
    """Create explicit input state for examples and tests."""

    return {
        "request": request,
        "normalized_request": "",
        "risk_score": 0,
        "route": "fast_path",
        "response": "",
        "audit_log": [],
    }
