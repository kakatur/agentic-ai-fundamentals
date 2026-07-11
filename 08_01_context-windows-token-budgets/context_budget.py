from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContextItem:
    label: str
    text: str
    priority: int = 1
    pinned: bool = False

    @property
    def estimated_tokens(self) -> int:
        return estimate_tokens(self.text)


@dataclass(frozen=True)
class BudgetReport:
    selected: tuple[ContextItem, ...]
    dropped: tuple[ContextItem, ...]
    used_tokens: int
    max_tokens: int

    @property
    def remaining_tokens(self) -> int:
        return self.max_tokens - self.used_tokens


def estimate_tokens(text: str) -> int:
    words = text.split()
    return max(1, int(len(words) * 1.3))


def reserve_response_budget(context_window: int, response_tokens: int, safety_margin: int = 64) -> int:
    available = context_window - response_tokens - safety_margin
    if available <= 0:
        raise ValueError("response budget and safety margin exceed the context window")
    return available


def build_context(items: list[ContextItem], max_tokens: int) -> BudgetReport:
    ordered = sorted(
        enumerate(items),
        key=lambda pair: (not pair[1].pinned, -pair[1].priority, -pair[0]),
    )
    selected: list[ContextItem] = []
    dropped: list[ContextItem] = []
    used = 0

    for _, item in ordered:
        cost = item.estimated_tokens
        if used + cost <= max_tokens:
            selected.append(item)
            used += cost
        else:
            dropped.append(item)

    selected.sort(key=lambda item: items.index(item))
    dropped.sort(key=lambda item: items.index(item))
    return BudgetReport(tuple(selected), tuple(dropped), used, max_tokens)


def edge_load_context(system: str, selected: tuple[ContextItem, ...], user_request: str) -> str:
    critical = [item for item in selected if item.pinned]
    flexible = [item for item in selected if not item.pinned]
    parts = [f"SYSTEM:\n{system}"]
    if critical:
        parts.append("CRITICAL CONTEXT:\n" + "\n".join(f"- {item.text}" for item in critical))
    if flexible:
        parts.append("SUPPORTING CONTEXT:\n" + "\n".join(f"- {item.text}" for item in flexible))
    parts.append(f"USER REQUEST:\n{user_request}")
    return "\n\n".join(parts)
