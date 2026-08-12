from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence

Vector = Sequence[float]
Metric = Callable[[Vector, Vector], float]


def _check_vectors(left: Vector, right: Vector) -> None:
    if not left or len(left) != len(right):
        raise ValueError("vectors must have the same nonzero dimension")


def dot_product(left: Vector, right: Vector) -> float:
    _check_vectors(left, right)
    return sum(a * b for a, b in zip(left, right))


def cosine_similarity(left: Vector, right: Vector) -> float:
    product = dot_product(left, right)
    left_norm = math.sqrt(dot_product(left, left))
    right_norm = math.sqrt(dot_product(right, right))
    return 0.0 if left_norm == 0 or right_norm == 0 else product / (left_norm * right_norm)


def euclidean_distance(left: Vector, right: Vector) -> float:
    _check_vectors(left, right)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def l2_normalize(vector: Vector) -> list[float]:
    if not vector:
        raise ValueError("vector must have a nonzero dimension")
    norm = math.sqrt(sum(value * value for value in vector))
    return [0.0] * len(vector) if norm == 0 else [value / norm for value in vector]


def rank(
    query: Vector,
    items: Mapping[str, Vector],
    metric_name: str,
) -> list[tuple[str, float]]:
    metrics: dict[str, tuple[Metric, bool]] = {
        "cosine": (cosine_similarity, True),
        "dot": (dot_product, True),
        "euclidean": (euclidean_distance, False),
    }
    if metric_name not in metrics:
        raise ValueError(f"unknown metric: {metric_name}")
    metric, larger_is_better = metrics[metric_name]
    scores = ((name, metric(query, vector)) for name, vector in items.items())
    return sorted(scores, key=lambda result: result[1], reverse=larger_is_better)
