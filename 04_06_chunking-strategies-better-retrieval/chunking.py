from dataclasses import dataclass


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    start_word: int
    end_word: int
    parent_id: str | None = None


def window_chunks(text: str, size: int, overlap: int = 0, document_id: str = "doc") -> list[Chunk]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("require size > 0 and 0 <= overlap < size")
    words = text.split()
    chunks = []
    for start in range(0, len(words), size - overlap):
        end = min(start + size, len(words))
        chunks.append(Chunk(f"{document_id}:{start}:{end}", " ".join(words[start:end]), start, end, document_id))
        if end == len(words):
            break
    return chunks


def section_chunks(sections: list[tuple[str, str]], document_id: str = "doc") -> list[Chunk]:
    chunks = []
    offset = 0
    for heading, body in sections:
        words = f"{heading} {body}".split()
        end = offset + len(words)
        chunks.append(Chunk(f"{document_id}:{offset}:{end}", " ".join(words), offset, end, document_id))
        offset = end
    return chunks


def expand_parent(child: Chunk, parents: dict[str, str]) -> str:
    if child.parent_id is None:
        raise ValueError("child has no parent")
    return parents[child.parent_id]
