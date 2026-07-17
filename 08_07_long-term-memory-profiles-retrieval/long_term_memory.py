from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class MemoryRecord:
    user_id: str
    key: str
    value: str
    source: str
    confidence: float
    created_at: str


class LongTermMemory:
    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []

    def remember(self, user_id: str, key: str, value: str, source: str, confidence: float = 1.0) -> MemoryRecord:
        if not 0 <= confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        record = MemoryRecord(
            user_id=user_id,
            key=key,
            value=value,
            source=source,
            confidence=confidence,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._records.append(record)
        return record

    def profile(self, user_id: str, min_confidence: float = 0.0) -> dict[str, str]:
        result: dict[str, str] = {}
        for record in self._records:
            if record.user_id == user_id and record.confidence >= min_confidence:
                result[record.key] = record.value
        return result

    def retrieve(self, user_id: str, query: str, limit: int = 3) -> tuple[MemoryRecord, ...]:
        terms = set(query.lower().split())
        scored: list[tuple[int, MemoryRecord]] = []
        for record in self._records:
            if record.user_id != user_id:
                continue
            haystack = f"{record.key} {record.value}".lower().split()
            score = len(terms & set(haystack))
            if score:
                scored.append((score, record))
        scored.sort(key=lambda item: (item[0], item[1].confidence), reverse=True)
        return tuple(record for _, record in scored[:limit])

    def provenance(self, record: MemoryRecord) -> str:
        return f"{record.key} came from {record.source} with confidence {record.confidence:.2f}"
