from __future__ import annotations

from dataclasses import dataclass
from collections import Counter


@dataclass(frozen=True)
class TraceEvent:
    step: int
    agent: str
    action: str
    target: str | None = None
    state_version: int = 0
    message: str = ""


@dataclass(frozen=True)
class DebugFinding:
    severity: str
    code: str
    detail: str


def detect_repeated_handoffs(events: tuple[TraceEvent, ...], limit: int = 2) -> list[DebugFinding]:
    pairs = Counter((event.agent, event.target) for event in events if event.action == "handoff")
    findings = []
    for (agent, target), count in pairs.items():
        if target and count > limit:
            findings.append(
                DebugFinding("high", "handoff_loop", f"{agent} handed off to {target} {count} times")
            )
    return findings


def detect_stale_state(events: tuple[TraceEvent, ...]) -> list[DebugFinding]:
    findings = []
    last_version = -1
    for event in events:
        if event.state_version < last_version:
            findings.append(
                DebugFinding("medium", "state_regression", f"step {event.step} used older state")
            )
        last_version = max(last_version, event.state_version)
    return findings


def detect_unanswered_task(events: tuple[TraceEvent, ...]) -> list[DebugFinding]:
    if not any(event.action == "final_answer" for event in events):
        return [DebugFinding("high", "missing_final_answer", "trace ended without a final answer")]
    return []


def analyze_trace(events: tuple[TraceEvent, ...]) -> list[DebugFinding]:
    findings = []
    findings.extend(detect_repeated_handoffs(events))
    findings.extend(detect_stale_state(events))
    findings.extend(detect_unanswered_task(events))
    return findings


def sample_bad_trace() -> tuple[TraceEvent, ...]:
    return (
        TraceEvent(1, "coordinator", "handoff", "billing", 1, "refund request"),
        TraceEvent(2, "billing", "handoff", "coordinator", 2, "needs login context"),
        TraceEvent(3, "coordinator", "handoff", "billing", 2, "retry billing"),
        TraceEvent(4, "billing", "handoff", "coordinator", 1, "older state used"),
        TraceEvent(5, "coordinator", "handoff", "billing", 2, "retry again"),
    )
