from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class EmbeddingConfig:
    model_id: str = "token-hash-demo-v1"
    dimension: int = 16
    normalize: bool = True


class TokenHashEmbedder:
    """Deterministic teaching embedder; it does not learn semantic similarity."""

    def __init__(self, config: EmbeddingConfig):
        if config.dimension <= 0:
            raise ValueError("dimension must be positive")
        self.config = config

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.config.dimension
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.config.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign
        if self.config.normalize:
            return l2_normalize(vector)
        return vector


def l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    return [0.0] * len(vector) if norm == 0 else [value / norm for value in vector]


def dot(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vectors must have the same dimension")
    return sum(a * b for a, b in zip(left, right))
