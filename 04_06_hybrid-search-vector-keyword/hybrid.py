"""A small hybrid retrieval example using DuckDB."""
import duckdb

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DIMENSIONS = 384


def connect(path):
    return duckdb.connect(str(path))


def build(con, documents, vectors, model=MODEL):
    """Replace the corpus and its embeddings as one transaction.

    Each document is (id, collection, text); vectors correspond in that order.
    Rebuild the FTS index after changes; DuckDB's index is a snapshot.
    """
    if len(documents) != len(vectors) or not documents:
        raise ValueError("provide one embedding for every document")
    if len({d[0] for d in documents}) != len(documents):
        raise ValueError("document IDs must be unique")
    if any(len(v) != DIMENSIONS for v in vectors):
        raise ValueError("wrong embedding dimension")
    con.execute("INSTALL fts; LOAD fts")
    con.execute("BEGIN TRANSACTION")
    try:
        con.execute("DROP TABLE IF EXISTS documents")
        con.execute(f"CREATE TABLE documents (id VARCHAR PRIMARY KEY, collection VARCHAR, body VARCHAR, embedding FLOAT[{DIMENSIONS}], model VARCHAR)")
        con.executemany("INSERT INTO documents VALUES (?, ?, ?, ?, ?)", [(*d, list(map(float, v)), model) for d, v in zip(documents, vectors)])
        con.execute("PRAGMA create_fts_index('documents', 'id', 'body', ignore='(\\.|[^a-zA-Z0-9])+', overwrite=1)")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise


def fuse(rankings, k=60):
    if k < 0:
        raise ValueError("k must be nonnegative")
    scores = {}
    for ranking in rankings:
        seen = set()
        for rank, doc_id in enumerate(ranking, 1):
            if doc_id not in seen:
                scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
                seen.add(doc_id)
    return sorted(scores.items(), key=lambda x: (-x[1], x[0]))


def search(con, query, vector, collection, limit=5, candidates=10, model=MODEL):
    if not query.strip() or len(vector) != DIMENSIONS or limit < 1 or candidates < 1:
        raise ValueError("query, vector, and positive limits are required")
    models = con.execute("SELECT DISTINCT model FROM documents").fetchall()
    if models != [(model,)]:
        raise ValueError("query and stored embedding models must match")
    dense = con.execute(f"""SELECT id, array_cosine_similarity(embedding, ?::FLOAT[{DIMENSIONS}]) AS score
        FROM documents WHERE collection = ? ORDER BY score DESC, id LIMIT ?""", [list(map(float, vector)), collection, candidates]).fetchall()
    lexical = con.execute("""SELECT id, score FROM (
        SELECT id, fts_main_documents.match_bm25(id, ?) AS score
        FROM documents WHERE collection = ?)
        WHERE score IS NOT NULL ORDER BY score DESC, id LIMIT ?""", [query, collection, candidates]).fetchall()
    fused = fuse([[row[0] for row in dense], [row[0] for row in lexical]])[:limit]
    return dense, lexical, fused
