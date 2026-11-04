"""Compare chunking strategies using local embeddings and DuckDB search."""

import json
import re

import duckdb

from chunking import TextChunk, chunk_text


SOURCE_ID = "refund-procedure-001"
HEADING = "Refunds after a duplicate charge"
DOCUMENT_TITLE = HEADING
BODY = (
    "First, confirm that both transactions have settled. "
    "Then refund the duplicate charge and tell the customer the refund "
    "should appear within five business days."
)
QUERY = (
    "A customer was charged twice. What steps should I follow, "
    "and what refund timing should I tell them?"
)


MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"


def load_model():
    """Load the local embedding model when the demo runs."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_ID, revision=MODEL_REVISION)


def procedure_metadata(source_id: str) -> dict[str, str]:
    return {
        "document_id": source_id,
        "document_title": DOCUMENT_TITLE,
        "section_heading": HEADING,
    }


def sentence_chunks(text: str, *, source_id: str) -> list[TextChunk]:
    """Split at sentence-ending punctuation and retain word offsets."""
    chunks = []
    for match in re.finditer(r"[^.!?]+[.!?]?(?:\s+|$)", text):
        sentence = match.group().strip()
        if not sentence:
            continue
        start = len(text[:match.start()].split())
        end = start + len(sentence.split())
        chunks.append(TextChunk(
            chunk_id=f"{source_id}:sentence-{len(chunks) + 1}",
            start_word=start,
            end_word=end,
            text=sentence,
            metadata={
                **procedure_metadata(source_id),
                "chunk_index": len(chunks) + 1,
            },
        ))
    return chunks


def paragraph_chunk(text: str, *, source_id: str) -> list[TextChunk]:
    """Keep the paragraph searchable and carry its heading as metadata."""
    return [TextChunk(
        chunk_id=f"{source_id}:section-1",
        start_word=0,
        end_word=len(text.split()),
        text=text,
        metadata={**procedure_metadata(source_id), "chunk_index": 1},
    )]


def build_chunk_table(
    connection: duckdb.DuckDBPyConnection,
    chunks_by_strategy: list[tuple[str, list[TextChunk]]],
    model,
    dimension: int,
) -> None:
    """Embed each search chunk and keep its source fields beside the vector."""
    connection.execute(
        f"CREATE TABLE chunks (strategy VARCHAR, chunk_id VARCHAR, text VARCHAR, "
        f"metadata_json VARCHAR, embedding FLOAT[{dimension}])"
    )
    rows = []
    for strategy, chunks in chunks_by_strategy:
        vectors = model.encode_document([chunk.text for chunk in chunks])
        for chunk, vector in zip(chunks, vectors, strict=True):
            rows.append((
                strategy, chunk.chunk_id, chunk.text,
                json.dumps(chunk.metadata), vector.tolist(),
            ))
    connection.executemany("INSERT INTO chunks VALUES (?, ?, ?, ?, ?)", rows)


def search_chunks(
    connection: duckdb.DuckDBPyConnection,
    strategy: str,
    query_vector: list[float],
    limit: int = 2,
) -> list[tuple[str, str, dict, float]]:
    """Rank stored vectors by exact cosine similarity to the query vector."""
    dimension = len(query_vector)
    rows = connection.execute(
        f"SELECT chunk_id, text, metadata_json, "
        f"array_cosine_similarity(embedding, ?::FLOAT[{dimension}]) AS score "
        "FROM chunks WHERE strategy = ? ORDER BY score DESC, chunk_id LIMIT ?",
        [query_vector, strategy, limit],
    ).fetchall()
    return [(chunk_id, text, json.loads(metadata), score)
            for chunk_id, text, metadata, score in rows]


def show_results(
    label: str,
    strategy: str,
    connection: duckdb.DuckDBPyConnection,
    query_vector: list[float],
) -> None:
    print(f"\n{label}")
    for chunk_id, text, metadata, score in search_chunks(connection, strategy, query_vector):
        print(
            f"  cosine_similarity={score:.3f}  {chunk_id}: {text}"
            f"  metadata={metadata}"
        )


def show_overlap_comparison(text: str, *, metadata: dict[str, str]) -> None:
    """Show the size and content effect of overlap on the same procedure."""
    print("\n4) Fixed windows: overlap comparison (8 words per chunk)")
    for overlap in (0, 3):
        chunks = chunk_text(
            text,
            source_id=f"{SOURCE_ID}:overlap-{overlap}",
            chunk_size=8,
            overlap=overlap,
            metadata=metadata,
        )
        label = "no overlap" if overlap == 0 else f"{overlap}-word overlap"
        print(f"  {label}: {len(chunks)} chunks ({len(chunks)} vectors if embedded)")
        for chunk in chunks[:2]:
            print(f"    {chunk.chunk_id}: {chunk.text}")


def main() -> None:
    print("SCENARIO: Internal application for customer service agents")
    print("INTERNAL PROCEDURE")
    print(f"  {HEADING}")
    print(f"  {BODY}")
    print(f"\nAGENT QUERY: {QUERY}")
    print(f"Embedding model: {MODEL_ID}")
    print("Score: cosine similarity between the query and stored chunk embeddings.")

    chunks_by_strategy = [
        ("fixed", chunk_text(
            BODY,
            source_id=SOURCE_ID,
            chunk_size=8,
            metadata=procedure_metadata(SOURCE_ID),
        )),
        ("sentence", sentence_chunks(BODY, source_id=SOURCE_ID)),
        ("paragraph", paragraph_chunk(BODY, source_id=SOURCE_ID)),
    ]
    model = load_model()
    query_vector = model.encode_query(QUERY).tolist()
    with duckdb.connect(":memory:") as connection:
        build_chunk_table(connection, chunks_by_strategy, model, len(query_vector))
        for number, (strategy, label) in enumerate((
            ("fixed", "Fixed windows: 8 words, no overlap"),
            ("sentence", "Sentence units"),
            ("paragraph", "Paragraph with heading metadata (one section)"),
        ), start=1):
            show_results(f"{number}) {label}", strategy, connection, query_vector)
    show_overlap_comparison(BODY, metadata=procedure_metadata(SOURCE_ID))
    print(
        "\nCompare which parts of the procedure each strategy keeps together. "
        "Sentence chunks keep individual sentences intact; the section contains both "
        "sentences, with the heading available as metadata. Three-word overlap "
        "carries words across window boundaries and increases this procedure from three chunks to five."
    )


if __name__ == "__main__":
    main()
