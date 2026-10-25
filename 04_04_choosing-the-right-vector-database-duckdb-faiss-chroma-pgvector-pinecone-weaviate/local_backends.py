"""Small FAISS adapter around an application-owned record shape."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class SearchRecord:
    record_id: str
    document: str
    embedding: tuple[float, ...]
    metadata: dict[str, str | int | float | bool]
    embedding_version: str
    name: str = ""


@dataclass(frozen=True)
class SearchHit:
    record_id: str
    document: str
    metadata: dict[str, str | int | float | bool]
    score: float
    name: str = ""


def validate_record(record: SearchRecord, dimension: int) -> None:
    if not record.record_id.strip() or not record.document.strip():
        raise ValueError("record ID and document are required")
    if not record.embedding_version.strip():
        raise ValueError("embedding version is required")
    if len(record.embedding) != dimension:
        raise ValueError("embedding dimension does not match the adapter")
    if any(not isfinite(value) for value in record.embedding):
        raise ValueError("embedding values must be finite")
    if any(not isinstance(value, (str, int, float, bool)) for value in record.metadata.values()):
        raise ValueError("metadata values must be strings, numbers, or booleans")


class FaissAdapter:
    """Exact flat-L2 index with an explicit mapping to stable application IDs."""

    def __init__(self, dimension: int) -> None:
        if dimension < 1:
            raise ValueError("dimension must be positive")
        import faiss

        self._np = __import__("numpy")
        self.dimension = dimension
        self._index = faiss.IndexIDMap2(faiss.IndexFlatL2(dimension))
        self._next_label = 0
        self._labels: dict[str, int] = {}
        self._records: dict[int, SearchRecord] = {}

    def upsert(self, record: SearchRecord) -> None:
        validate_record(record, self.dimension)
        np = self._np
        previous = self._labels.pop(record.record_id, None)
        if previous is not None:
            self._index.remove_ids(np.asarray([previous], dtype="int64"))
            self._records.pop(previous)
        label = self._next_label
        self._next_label += 1
        vector = np.asarray([record.embedding], dtype="float32")
        self._index.add_with_ids(vector, np.asarray([label], dtype="int64"))
        self._labels[record.record_id] = label
        self._records[label] = record

    def delete(self, record_id: str) -> bool:
        label = self._labels.pop(record_id, None)
        if label is None:
            return False
        self._index.remove_ids(self._np.asarray([label], dtype="int64"))
        self._records.pop(label)
        return True

    def search(
        self,
        query: tuple[float, ...],
        *,
        filters: dict[str, str | int | float | bool],
        limit: int = 3,
    ) -> list[SearchHit]:
        if len(query) != self.dimension or any(not isfinite(value) for value in query):
            raise ValueError("query must be a finite vector with the configured dimension")
        if limit < 1:
            raise ValueError("limit must be positive")
        if self._index.ntotal == 0:
            return []
        vector = self._np.asarray([query], dtype="float32")
        # This adapter post-filters an exhaustive result set. A
        # production ANN system needs a deliberate filtered-search strategy.
        distances, labels = self._index.search(vector, self._index.ntotal)
        hits = []
        for distance, label in zip(distances[0], labels[0]):
            record = self._records.get(int(label))
            if record is not None and all(record.metadata.get(key) == value for key, value in filters.items()):
                hits.append(SearchHit(record.record_id, record.document, dict(record.metadata), float(distance), record.name))
        return hits[:limit]
