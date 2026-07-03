from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    conversation_id: str
    role: str
    content: str


class ConversationStore:
    def __init__(self, database: str) -> None:
        self.connection = sqlite3.connect(database)
        self.connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL
                )
                """
            )

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        if role not in {"user", "assistant", "system"}:
            raise ValueError("role must be user, assistant, or system")
        with self.connection:
            self.connection.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                (conversation_id, role, content),
            )

    def list_messages(self, conversation_id: str) -> list[Message]:
        rows = self.connection.execute(
            "SELECT conversation_id, role, content FROM messages WHERE conversation_id = ? ORDER BY id",
            (conversation_id,),
        ).fetchall()
        return [Message(row["conversation_id"], row["role"], row["content"]) for row in rows]

    def search_content(self, term: str) -> list[Message]:
        rows = self.connection.execute(
            "SELECT conversation_id, role, content FROM messages WHERE content LIKE ? ORDER BY id",
            (f"%{term}%",),
        ).fetchall()
        return [Message(row["conversation_id"], row["role"], row["content"]) for row in rows]

    def close(self) -> None:
        self.connection.close()
