from __future__ import annotations
from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class Record:
    record_id: str
    text: str
    vector: tuple[float, ...]
    tenant: str
    embedding_version: str

class ExactVectorStore:
    def __init__(self, dimension, embedding_version):
        self.dimension, self.embedding_version = dimension, embedding_version
        self._records = {}
    def upsert(self, record):
        if len(record.vector) != self.dimension: raise ValueError("dimension mismatch")
        if record.embedding_version != self.embedding_version: raise ValueError("embedding version mismatch")
        self._records[record.record_id] = record
    def delete(self, record_id): self._records.pop(record_id, None)
    def query(self, vector, tenant, limit=3):
        if len(vector) != self.dimension: raise ValueError("dimension mismatch")
        def cosine(other):
            denom=sqrt(sum(x*x for x in vector))*sqrt(sum(x*x for x in other))
            return 0.0 if denom == 0 else sum(x*y for x,y in zip(vector,other))/denom
        eligible=(r for r in self._records.values() if r.tenant == tenant)
        return sorted(((r.record_id, cosine(r.vector)) for r in eligible), key=lambda x:x[1], reverse=True)[:limit]
