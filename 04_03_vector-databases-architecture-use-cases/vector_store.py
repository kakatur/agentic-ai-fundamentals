"""A small exact-search store for teaching record lifecycle contracts."""

from dataclasses import dataclass
from math import isfinite, sqrt


@dataclass(frozen=True)
class VectorRecord:
    """A source record paired with its embedding and product."""

    record_id: str
    product: str
    text: str
    embedding: tuple[float, ...]
    embedding_version: str


class ExactVectorStore:
    """Store records by ID and rank eligible records exactly."""

    def __init__(self, dimension: int, *, expected_embedding_version: str) -> None:
        if dimension < 1:
            raise ValueError("dimension must be positive")
        if not expected_embedding_version:
            raise ValueError("expected embedding version is required")
        self.dimension = dimension
        self.expected_embedding_version = expected_embedding_version
        self._records: dict[str, VectorRecord] = {}

    def upsert(self, record: VectorRecord) -> None:
        if not _has_valid_record_data(record):
            raise ValueError("record fields must be present; embedding must be finite and nonzero")
        if len(record.embedding) != self.dimension:
            raise ValueError("embedding dimension does not match the store")
        if record.embedding_version != self.expected_embedding_version:
            raise ValueError("embedding version does not match the store")
        self._records[record.record_id] = record

    def delete(self, record_id: str) -> bool:
        """Remove a record; return whether the ID existed."""
        return self._records.pop(record_id, None) is not None

    def search(
        self,
        query: tuple[float, ...],
        *,
        product: str,
        limit: int = 3,
    ) -> list[tuple[VectorRecord, float]]:
        """Return exact matches for the requested product.

        This teaching implementation applies the product eligibility condition
        before cosine scoring and exhaustively scores every eligible record.
        Other exact or ANN backends may execute filters differently while
        preserving the same eligibility rule for returned results.
        """
        if len(query) != self.dimension:
            raise ValueError("query dimension does not match the store")
        if not all(isfinite(value) for value in query):
            raise ValueError("query vector values must be finite")
        if not product:
            raise ValueError("product is required")
        if limit < 1:
            raise ValueError("limit must be positive")
        query_norm = sqrt(sum(value * value for value in query))
        if query_norm == 0:
            raise ValueError("query vector must not be zero")

        eligible_records = (
            record
            for record in self._records.values()
            if record.product == product
        )
        ranked = []
        for record in eligible_records:
            record_norm = sqrt(sum(value * value for value in record.embedding))
            dot = sum(a * b for a, b in zip(query, record.embedding))
            score = dot / (query_norm * record_norm)
            ranked.append((record, score))

        ranked.sort(key=lambda item: (-item[1], item[0].record_id))
        return ranked[:limit]


def _has_finite_nonzero_embedding(embedding: tuple[float, ...]) -> bool:
    return (
        bool(embedding)
        and all(isfinite(value) for value in embedding)
        and any(value != 0.0 for value in embedding)
    )


def _has_valid_record_data(record: VectorRecord) -> bool:
    return (
        bool(record.record_id)
        and bool(record.product)
        and bool(record.text.strip())
        and _has_finite_nonzero_embedding(record.embedding)
    )
