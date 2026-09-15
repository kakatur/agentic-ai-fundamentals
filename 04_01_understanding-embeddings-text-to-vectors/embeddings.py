from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence


MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
EMBEDDING_DIMENSION = 384


class EmbeddingModel(Protocol):
    def encode_query(self, sentences: Sequence[str], **kwargs: object) -> object: ...

    def encode_document(self, sentences: Sequence[str], **kwargs: object) -> object: ...


@dataclass(frozen=True)
class EmbeddedText:
    text: str
    role: str
    values: tuple[float, ...]


def load_model() -> EmbeddingModel:
    """Load the exact model revision, downloading it once and then using the cache."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_ID, revision=MODEL_REVISION)


def embed_texts(
    model: EmbeddingModel,
    texts: Sequence[str],
    *,
    role: str,
    expected_dimension: int = EMBEDDING_DIMENSION,
) -> list[EmbeddedText]:
    """Encode query or document text with the model's retrieval methods."""
    if role not in {"query", "document"}:
        raise ValueError("role must be 'query' or 'document'")
    if not texts or any(not text.strip() for text in texts):
        raise ValueError("texts must contain non-empty strings")

    encoder = model.encode_query if role == "query" else model.encode_document
    matrix = encoder(
        list(texts),
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    embedded: list[EmbeddedText] = []
    for text, vector in zip(texts, matrix, strict=True):
        values = tuple(float(value) for value in vector)
        if len(values) != expected_dimension:
            raise ValueError(
                f"expected {expected_dimension} dimensions, received {len(values)}"
            )
        embedded.append(EmbeddedText(text, role, values))
    return embedded


def cosine_similarity(left: EmbeddedText, right: EmbeddedText) -> float:
    if len(left.values) != len(right.values):
        raise ValueError("cosine similarity requires vectors of equal length")
    dot_product = sum(a * b for a, b in zip(left.values, right.values, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left.values))
    right_norm = math.sqrt(sum(value * value for value in right.values))
    if left_norm == 0.0 or right_norm == 0.0:
        raise ValueError("cosine similarity is undefined for a zero vector")
    return dot_product / (left_norm * right_norm)


def rank_documents(
    query: EmbeddedText, documents: Iterable[EmbeddedText]
) -> list[tuple[float, EmbeddedText]]:
    if query.role != "query":
        raise ValueError("rank_documents expects a query embedding")
    scored: list[tuple[float, EmbeddedText]] = []
    for document in documents:
        if document.role != "document":
            raise ValueError("rank_documents expects document embeddings")
        scored.append((cosine_similarity(query, document), document))
    return sorted(scored, key=lambda item: item[0], reverse=True)


def exact_token_overlap(left: str, right: str) -> set[str]:
    """A deliberately small keyword baseline for the demo."""
    tokenize = lambda text: set(re.findall(r"[a-z0-9]+", text.lower()))
    return tokenize(left) & tokenize(right)
