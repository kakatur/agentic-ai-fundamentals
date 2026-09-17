from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence


@dataclass(frozen=True)
class SearchRecord:
    record_id: str
    document: str
    embedding: Sequence[float]
    metadata: dict[str, str]


def validate_batch(records: Sequence[SearchRecord]) -> int:
    if not records:
        raise ValueError("records cannot be empty")
    dimension = len(records[0].embedding)
    if dimension == 0 or any(len(record.embedding) != dimension for record in records):
        raise ValueError("embeddings must have one nonzero dimension")
    if len({record.record_id for record in records}) != len(records):
        raise ValueError("record IDs must be unique within a batch")
    return dimension


def build_faiss_l2_index(records: Sequence[SearchRecord]) -> tuple[Any, list[str]]:
    dimension = validate_batch(records)
    try:
        import faiss
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("install numpy and faiss-cpu for the FAISS path") from exc

    matrix = np.asarray([record.embedding for record in records], dtype="float32")
    index = faiss.IndexFlatL2(dimension)
    index.add(matrix)
    return index, [record.record_id for record in records]


def upsert_chroma(collection: Any, records: Sequence[SearchRecord]) -> None:
    validate_batch(records)
    collection.upsert(
        ids=[record.record_id for record in records],
        documents=[record.document for record in records],
        embeddings=[list(record.embedding) for record in records],
        metadatas=[record.metadata for record in records],
    )
