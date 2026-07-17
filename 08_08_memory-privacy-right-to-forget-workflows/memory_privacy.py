from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class PrivateMemory:
    memory_id: str
    user_id: str
    category: str
    value: str
    consent: bool


@dataclass(frozen=True)
class AuditEvent:
    action: str
    user_id: str
    detail: str
    timestamp: str


class PrivacyAwareMemoryStore:
    def __init__(self) -> None:
        self._memories: dict[str, PrivateMemory] = {}
        self._audit: list[AuditEvent] = []
        self._suppressed_users: set[str] = set()

    def remember(self, memory: PrivateMemory) -> None:
        if memory.user_id in self._suppressed_users:
            raise ValueError("user memory is suppressed")
        if not memory.consent:
            raise ValueError("cannot store memory without consent")
        self._memories[memory.memory_id] = memory
        self._log("remember", memory.user_id, memory.memory_id)

    def export_user(self, user_id: str) -> tuple[PrivateMemory, ...]:
        self._log("export", user_id, "exported user memories")
        return tuple(memory for memory in self._memories.values() if memory.user_id == user_id)

    def delete_user(self, user_id: str) -> int:
        memory_ids = [memory_id for memory_id, memory in self._memories.items() if memory.user_id == user_id]
        for memory_id in memory_ids:
            del self._memories[memory_id]
        self._suppressed_users.add(user_id)
        self._log("delete", user_id, f"deleted {len(memory_ids)} memories and suppressed future writes")
        return len(memory_ids)

    def audit_log(self, user_id: str | None = None) -> tuple[AuditEvent, ...]:
        if user_id is None:
            return tuple(self._audit)
        return tuple(event for event in self._audit if event.user_id == user_id)

    def _log(self, action: str, user_id: str, detail: str) -> None:
        self._audit.append(AuditEvent(action, user_id, detail, datetime.now(timezone.utc).isoformat()))
