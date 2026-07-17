from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True)
class CacheEntry:
    prompt: str
    response: str
    safety_label: str = "general"


@dataclass(frozen=True)
class CacheHit:
    entry: CacheEntry
    score: float


def tokenize(text: str) -> list[str]:
    return [token.strip(".,!?;:()[]{}").lower() for token in text.split() if token.strip(".,!?;:()[]{}")]


def cosine_similarity(left: str, right: str) -> float:
    a = Counter(tokenize(left))
    b = Counter(tokenize(right))
    if not a or not b:
        return 0.0
    dot = sum(a[token] * b[token] for token in a.keys() & b.keys())
    norm_a = sqrt(sum(value * value for value in a.values()))
    norm_b = sqrt(sum(value * value for value in b.values()))
    return dot / (norm_a * norm_b)


class SemanticCache:
    def __init__(self, threshold: float = 0.75) -> None:
        self.threshold = threshold
        self._entries: list[CacheEntry] = []

    def add(self, prompt: str, response: str, safety_label: str = "general") -> None:
        self._entries.append(CacheEntry(prompt, response, safety_label))

    def lookup(self, prompt: str, safety_label: str = "general") -> CacheHit | None:
        candidates = [
            CacheHit(entry, cosine_similarity(prompt, entry.prompt))
            for entry in self._entries
            if entry.safety_label == safety_label
        ]
        if not candidates:
            return None
        best = max(candidates, key=lambda hit: hit.score)
        if best.score < self.threshold:
            return None
        return best
