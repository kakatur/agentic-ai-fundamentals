"""Compare chunking strategies for one internal support-agent question.

The demo counts distinct query words and prints text, metadata, and chunk IDs
so learners can inspect what each strategy makes available to search.
"""

import re

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


def words(text: str) -> set[str]:
    """Return lowercase word terms, ignoring punctuation."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


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


def show_results(label: str, chunks: list[TextChunk], query_terms: set[str]) -> None:
    ranked = sorted(
        ((len(query_terms & words(chunk.text)), chunk) for chunk in chunks),
        key=lambda item: (-item[0], item[1].chunk_id),
    )
    print(f"\n{label}")
    for score, chunk in ranked[:2]:
        print(
            f"  word_overlap={score}  {chunk.chunk_id}: {chunk.text}"
            f"  metadata={chunk.metadata}"
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
    print("Score: number of distinct question words found in each chunk.")

    query_terms = words(QUERY)
    show_results(
        "1) Fixed windows: 8 words, no overlap",
        chunk_text(
            BODY,
            source_id=SOURCE_ID,
            chunk_size=8,
            metadata=procedure_metadata(SOURCE_ID),
        ),
        query_terms,
    )
    show_results(
        "2) Sentence units",
        sentence_chunks(BODY, source_id=SOURCE_ID),
        query_terms,
    )
    show_results(
        "3) Paragraph with heading metadata (one section)",
        paragraph_chunk(BODY, source_id=SOURCE_ID),
        query_terms,
    )
    show_overlap_comparison(BODY, metadata=procedure_metadata(SOURCE_ID))
    print(
        "\nCompare which parts of the procedure each strategy keeps together. "
        "Sentence chunks keep individual sentences intact; the section contains both "
        "sentences, with the heading available as metadata. Three-word overlap "
        "carries words across window boundaries and increases this procedure from three chunks to five."
    )


if __name__ == "__main__":
    main()
