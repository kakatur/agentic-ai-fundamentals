"""Store and retrieve conversation messages using SQLite."""
import sqlite3


def create_schema(connection: sqlite3.Connection) -> None:
    connection.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, conversation_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL)')
    connection.commit()


def add_messages(connection: sqlite3.Connection, conversation_id: str, messages: list[tuple[str, str]]) -> None:
    """Commit the whole batch or roll it back on an exception."""
    with connection:
        connection.executemany('INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)',
                               [(conversation_id, role, content) for role, content in messages])


def get_messages(connection: sqlite3.Connection, conversation_id: str) -> list[tuple[str, str]]:
    rows = connection.execute('SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id',
                              (conversation_id,)).fetchall()
    return rows
