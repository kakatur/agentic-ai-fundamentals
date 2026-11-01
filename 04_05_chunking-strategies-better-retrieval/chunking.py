"""A transparent whitespace-word chunking baseline with source offsets."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    chunk_id: str
    start_word: int
    end_word: int
    text: str


def chunk_text(text: str, *, source_id: str, chunk_size: int, overlap: int = 0) -> list[TextChunk]:
    """Split text into whitespace-delimited word windows.

    Offsets are positions of whitespace-separated words in the source, with an
    exclusive end. Use the selected embedding model's tokenizer to set a
    production token budget.
    """
    if not source_id.strip():
        raise ValueError("source_id must not be empty")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be nonnegative and smaller than chunk_size")

    words = text.split()
    step = chunk_size - overlap
    chunks: list[TextChunk] = []
    for start in range(0, len(words), step):
        end = min(start + chunk_size, len(words))
        chunks.append(TextChunk(
            chunk_id=f"{source_id}:{start}-{end}",
            start_word=start,
            end_word=end,
            text=" ".join(words[start:end]),
        ))
        if end == len(words):
            break
    return chunks
