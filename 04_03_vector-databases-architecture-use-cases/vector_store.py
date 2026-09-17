from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt


@dataclass(frozen=True)
class Record:
    record_id: str
    text: str
    vector: tuple[float, ...]
    tenant_id: str
    embedding_version: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchHit:
    record_id: str
    score: float
    text: str


class ExactVectorStore:
    """Small exact store that makes the vector-record lifecycle visible."""

    def __init__(self, dimension: int, embedding_version: str):
        if dimension <= 0:
            raise ValueError("dimension must be positive")
        self.dimension = dimension
        self.embedding_version = embedding_version
        self._records: dict[str, Record] = {}

    def upsert(self, record: Record) -> None:
        self._validate_vector(record.vector)
        if record.embedding_version != self.embedding_version:
            raise ValueError("embedding version mismatch")
        self._records[record.record_id] = record

    def delete(self, record_id: str) -> bool:
        return self._records.pop(record_id, None) is not None

    def query(
        self,
        vector: tuple[float, ...],
        *,
        tenant_id: str,
        metadata_filter: dict[str, str] | None = None,
        limit: int = 3,
    ) -> list[SearchHit]:
        self._validate_vector(vector)
        if limit <= 0:
            raise ValueError("limit must be positive")

        required = metadata_filter or {}
        eligible = (
            record
            for record in self._records.values()
            if record.tenant_id == tenant_id
            and all(record.metadata.get(key) == value for key, value in required.items())
        )
        hits = [
            SearchHit(record.record_id, _cosine(vector, record.vector), record.text)
            for record in eligible
        ]
        return sorted(hits, key=lambda hit: (-hit.score, hit.record_id))[:limit]

    def _validate_vector(self, vector: tuple[float, ...]) -> None:
        if len(vector) != self.dimension:
            raise ValueError("dimension mismatch")


def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)
