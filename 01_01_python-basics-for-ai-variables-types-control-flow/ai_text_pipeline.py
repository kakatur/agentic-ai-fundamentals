from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AIRequest:
    raw_text: str
    normalized_text: str
    intent: str
    token_estimate: int
    valid: bool


def normalize_text(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("value must be a string")
    return " ".join(value.strip().split())


def estimate_tokens(text: str) -> int:
    words = normalize_text(text).split()
    return max(1, round(len(words) * 1.3)) if words else 0


def classify_intent(text: str) -> str:
    normalized = normalize_text(text).lower()
    if not normalized:
        return "empty"
    if "summarize" in normalized or "summary" in normalized:
        return "summarize"
    if "translate" in normalized:
        return "translate"
    if "extract" in normalized or "invoice" in normalized:
        return "extract"
    return "chat"


def build_request(text: str) -> AIRequest:
    normalized = normalize_text(text)
    return AIRequest(
        raw_text=text,
        normalized_text=normalized,
        intent=classify_intent(normalized),
        token_estimate=estimate_tokens(normalized),
        valid=bool(normalized),
    )


def classify_requests(values: list[str]) -> list[AIRequest]:
    results: list[AIRequest] = []
    for value in values:
        request = build_request(value)
        if request.valid:
            results.append(request)
    return results
