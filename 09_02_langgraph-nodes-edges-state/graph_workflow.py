"""Deterministic graph workflow used to teach LangGraph core concepts.

The classes in this file intentionally mirror the mental model behind
LangGraph: typed state, node functions, normal edges, conditional edges, and
reducers. They are not a replacement for LangGraph. They keep the mechanics
small enough for tests and a classroom walkthrough.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable


START = "__start__"
END = "__end__"


@dataclass(frozen=True)
class SupportState:
    """Shared workflow state passed from node to node."""

    request: str
    customer_tier: str = "standard"
    route: str | None = None
    facts: tuple[str, ...] = ()
    draft: str | None = None
    risk: int = 0
    final_answer: str | None = None
    history: tuple[str, ...] = ()


@dataclass(frozen=True)
class NodeResult:
    """Patch returned by a node.

    Nodes return partial state updates.
    This patch keeps merge behavior explicit.
    """

    route: str | None = None
    facts: tuple[str, ...] = ()
    draft: str | None = None
    risk: int | None = None
    final_answer: str | None = None
    history: tuple[str, ...] = ()


Node = Callable[[SupportState], NodeResult]
Condition = Callable[[SupportState], str]


class StateGraph:
    """Small graph runner with LangGraph-like concepts."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, str] = {}
        self._conditional_edges: dict[str, tuple[Condition, dict[str, str]]] = {}
        self._entry_point: str | None = None

    def add_node(self, name: str, node: Node) -> None:
        if name in {START, END}:
            raise ValueError(f"{name!r} is reserved")
        self._nodes[name] = node

    def set_entry_point(self, name: str) -> None:
        self._require_node(name)
        self._entry_point = name
        self._edges[START] = name

    def add_edge(self, source: str, target: str) -> None:
        self._require_known_endpoint(source)
        self._require_known_endpoint(target)
        self._edges[source] = target

    def add_conditional_edges(
        self,
        source: str,
        condition: Condition,
        branches: dict[str, str],
    ) -> None:
        self._require_node(source)
        if not branches:
            raise ValueError("conditional edges need at least one branch")
        for target in branches.values():
            self._require_known_endpoint(target)
        self._conditional_edges[source] = (condition, branches)

    def compile(self) -> CompiledGraph:
        if self._entry_point is None:
            raise ValueError("set_entry_point() must be called before compile()")
        return CompiledGraph(
            nodes=dict(self._nodes),
            edges=dict(self._edges),
            conditional_edges=dict(self._conditional_edges),
        )

    def _require_node(self, name: str) -> None:
        if name not in self._nodes:
            raise ValueError(f"unknown node: {name}")

    def _require_known_endpoint(self, name: str) -> None:
        if name == END:
            return
        self._require_node(name)


@dataclass(frozen=True)
class GraphRun:
    """Result returned after invoking a compiled graph."""

    state: SupportState
    visited: tuple[str, ...]


@dataclass(frozen=True)
class CompiledGraph:
    """Executable graph produced by StateGraph.compile()."""

    nodes: dict[str, Node]
    edges: dict[str, str]
    conditional_edges: dict[str, tuple[Condition, dict[str, str]]]

    def invoke(self, state: SupportState, *, max_steps: int = 20) -> GraphRun:
        current = self.edges[START]
        visited: list[str] = []

        for _ in range(max_steps):
            if current == END:
                return GraphRun(state=state, visited=tuple(visited))
            if current not in self.nodes:
                raise ValueError(f"graph reached unknown node: {current}")

            visited.append(current)
            state = merge_state(state, self.nodes[current](state), node_name=current)
            current = self._next_node(current, state)

        raise RuntimeError(f"graph did not reach END within {max_steps} steps")

    def _next_node(self, current: str, state: SupportState) -> str:
        if current in self.conditional_edges:
            condition, branches = self.conditional_edges[current]
            branch = condition(state)
            if branch not in branches:
                raise ValueError(f"condition returned unknown branch: {branch}")
            return branches[branch]
        return self.edges.get(current, END)


def merge_state(
    state: SupportState,
    patch: NodeResult,
    *,
    node_name: str,
) -> SupportState:
    """Merge a node patch into state.

    Scalars overwrite when the patch supplies a value.
    Tuple fields append like reducers.
    """

    return replace(
        state,
        route=patch.route
        if patch.route is not None
        else state.route,
        facts=state.facts + patch.facts,
        draft=patch.draft
        if patch.draft is not None
        else state.draft,
        risk=patch.risk
        if patch.risk is not None
        else state.risk,
        final_answer=patch.final_answer
        if patch.final_answer is not None
        else state.final_answer,
        history=state.history + (node_name,) + patch.history,
    )


def classify_request(state: SupportState) -> NodeResult:
    text = state.request.lower()
    billing_terms = ("refund", "charge", "invoice", "billing")
    security_terms = ("login", "password", "mfa", "security")
    if any(word in text for word in billing_terms):
        return NodeResult(
            route="billing",
            facts=("billing language detected",),
        )
    if any(word in text for word in security_terms):
        return NodeResult(
            route="security",
            facts=("account access language detected",),
        )
    return NodeResult(
        route="general",
        facts=("no specialist keywords found",),
    )


def retrieve_policy(state: SupportState) -> NodeResult:
    if state.route == "billing":
        return NodeResult(
            facts=("refunds require invoice id",),
        )
    if state.route == "security":
        return NodeResult(
            facts=("MFA reset requires identity check",),
        )
    return NodeResult(
        facts=("general support can answer simple how-to requests",),
    )


def draft_response(state: SupportState) -> NodeResult:
    if state.route == "billing":
        draft = "I can help review the charge after you provide the invoice id."
    elif state.route == "security":
        draft = (
            "Start with identity verification, then reset MFA from account "
            "settings."
        )
    else:
        draft = "I can answer this as a general support request."
    return NodeResult(draft=draft)


def review_risk(state: SupportState) -> NodeResult:
    text = state.request.lower()
    risk = 0
    if state.customer_tier == "enterprise":
        risk += 1
    risk_terms = ("urgent", "legal", "fraud", "angry")
    if any(word in text for word in risk_terms):
        risk += 2
    if state.route == "general":
        risk += 1
    return NodeResult(risk=risk)


def should_escalate(state: SupportState) -> str:
    return "escalate" if state.risk >= 2 else "finish"


def finalize_response(state: SupportState) -> NodeResult:
    facts = "; ".join(state.facts)
    return NodeResult(final_answer=f"{state.draft} Facts used: {facts}.")


def escalate_to_human(state: SupportState) -> NodeResult:
    return NodeResult(
        final_answer=(
            "Escalate to human review with the request, selected route, facts, "
            f"and risk score {state.risk}."
        ),
        history=("human_review",),
    )


def build_support_graph() -> CompiledGraph:
    graph = StateGraph()
    graph.add_node("classify", classify_request)
    graph.add_node("retrieve_policy", retrieve_policy)
    graph.add_node("draft_response", draft_response)
    graph.add_node("review_risk", review_risk)
    graph.add_node("finalize", finalize_response)
    graph.add_node("escalate", escalate_to_human)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "retrieve_policy")
    graph.add_edge("retrieve_policy", "draft_response")
    graph.add_edge("draft_response", "review_risk")
    graph.add_conditional_edges(
        "review_risk",
        should_escalate,
        {"finish": "finalize", "escalate": "escalate"},
    )
    graph.add_edge("finalize", END)
    graph.add_edge("escalate", END)
    return graph.compile()
