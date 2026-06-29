from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Callable


@dataclass(frozen=True)
class Message:
    sender: str
    text: str


@dataclass(frozen=True)
class WorkflowState:
    task_id: str
    request: str
    route: str | None = None
    messages: tuple[Message, ...] = ()
    facts: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    decision: str | None = None
    version: int = 0


@dataclass(frozen=True)
class StatePatch:
    route: str | None = None
    messages: tuple[Message, ...] = ()
    facts: tuple[str, ...] = ()
    risks: tuple[str, ...] = ()
    decision: str | None = None


def merge_state(state: WorkflowState, *patches: StatePatch) -> WorkflowState:
    route = state.route
    decision = state.decision
    messages = list(state.messages)
    facts = list(state.facts)
    risks = list(state.risks)

    for patch in patches:
        if patch.route is not None:
            route = patch.route
        if patch.decision is not None:
            decision = patch.decision
        messages.extend(patch.messages)
        facts.extend(item for item in patch.facts if item not in facts)
        risks.extend(item for item in patch.risks if item not in risks)

    return replace(
        state,
        route=route,
        decision=decision,
        messages=tuple(messages),
        facts=tuple(facts),
        risks=tuple(risks),
        version=state.version + 1,
    )


class Checkpointer:
    def __init__(self) -> None:
        self._snapshots: dict[str, list[WorkflowState]] = {}

    def save(self, state: WorkflowState) -> None:
        self._snapshots.setdefault(state.task_id, []).append(state)

    def latest(self, task_id: str) -> WorkflowState:
        return self._snapshots[task_id][-1]

    def history(self, task_id: str) -> tuple[WorkflowState, ...]:
        return tuple(self._snapshots.get(task_id, ()))


def route_agent(state: WorkflowState) -> StatePatch:
    text = state.request.lower()
    if "refund" in text or "invoice" in text:
        return StatePatch(route="billing", facts=("billing intent",))
    if "login" in text or "password" in text:
        return StatePatch(route="security", facts=("security intent",))
    return StatePatch(route="technical", facts=("fallback technical route",))


def risk_agent(state: WorkflowState) -> StatePatch:
    risks = []
    if "urgent" in state.request.lower():
        risks.append("urgent customer impact")
    if state.route == "billing":
        risks.append("money movement")
    return StatePatch(risks=tuple(risks))


def decision_agent(state: WorkflowState) -> StatePatch:
    if state.risks:
        return StatePatch(decision="review", messages=(Message("decision", "send to review"),))
    return StatePatch(decision="answer", messages=(Message("decision", "answer directly"),))


def run_workflow(initial: WorkflowState, checkpoint: Checkpointer) -> WorkflowState:
    checkpoint.save(initial)
    routed = merge_state(initial, route_agent(initial))
    checkpoint.save(routed)
    assessed = merge_state(routed, risk_agent(routed))
    checkpoint.save(assessed)
    final = merge_state(assessed, decision_agent(assessed))
    checkpoint.save(final)
    return final
