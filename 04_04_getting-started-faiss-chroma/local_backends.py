from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SearchRecord:
    record_id: str; document: str; embedding: list[float]; metadata: dict

def validate_batch(records):
    if not records: raise ValueError("records cannot be empty")
    dimension=len(records[0].embedding)
    if dimension == 0 or any(len(r.embedding)!=dimension for r in records): raise ValueError("embeddings must be rectangular")
    if len({r.record_id for r in records}) != len(records): raise ValueError("record IDs must be unique")

def build_faiss_index(records):
    validate_batch(records)
    try:
        import faiss
        import numpy as np
    except ImportError as exc: raise RuntimeError("install numpy and faiss-cpu for the FAISS path") from exc
    matrix=np.asarray([r.embedding for r in records],dtype="float32")
    index=faiss.IndexFlatL2(matrix.shape[1]); index.add(matrix)
    return index

def upsert_chroma(collection, records):
    validate_batch(records)
    collection.upsert(ids=[r.record_id for r in records], documents=[r.document for r in records], embeddings=[r.embedding for r in records], metadatas=[r.metadata for r in records])
