# Python and SQLite: Save and Retrieve Conversation History

Store conversation messages in SQLite, retrieve one conversation in insertion order, and test that a failed batch rolls back. The demo uses an in-memory database and makes no AI model call.

## Create and use a database

`sqlite3.connect(':memory:')` creates an in-memory database for this connection. It disappears when the connection closes. `create_schema` creates a `messages` table with an integer primary key, conversation ID, role, and content. The `NOT NULL` fields reject missing SQL values. The demo explicitly closes the connection in a `finally` block; a connection context manager handles transactions but does not itself close the connection.

## Insert a batch with parameters

`add_messages` uses `executemany` and `?` placeholders to bind each conversation ID, role, and message separately from the SQL text. For example, a conversation ID containing quotes is still treated as a value. Placeholders bind values, not table or column names.

The `with connection` block commits on success or rolls back on an exception when a transaction is open. The example uses the default connection transaction mode, explicitly commits schema creation first, and has no earlier uncommitted work. A test supplies a `None` content value after a valid row: the constraint raises `IntegrityError`, and neither row remains.

## Retrieve one conversation

`get_messages` binds the conversation ID and orders results by `id`. For the demo, it returns:

```text
[('user', 'Where is my order?'), ('assistant', 'It shipped today.')]
```

A different conversation ID returns an empty list. Ordering by ID makes the selected order explicit; without an `ORDER BY`, do not rely on a particular row order. This example is deliberately local and has no user authentication or authorization layer.

## Interview questions

- **Basic:** Why use placeholders in SQL? They bind data values separately from SQL text and avoid building queries by interpolating untrusted values.
- **Intermediate:** What does the connection context manager do? With an open transaction, it commits on successful exit and rolls back on an exception; it does not close the connection.
- **Advanced:** Why specify `ORDER BY` when reading history? SQL does not guarantee a result order without it. The application must choose a stable ordering that matches its needs.

## Run and test

Requires Python 3.10 or newer; no third-party packages are needed.

```bash
python3 demo.py
python3 -m unittest -v
```

Try adding a third message or an invalid `None` content value. Compare the stored results with the tests. The in-memory example does not persist after the connection closes.

Reference: Python sqlite3 [https://docs.python.org/3/library/sqlite3.html].
