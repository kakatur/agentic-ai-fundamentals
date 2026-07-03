from __future__ import annotations

from collections import Counter, defaultdict


def tokenize(text: str) -> list[str]:
    return [part.strip(".,!?;:").lower() for part in text.split() if part.strip(".,!?;:")]


def unique_terms(text: str) -> set[str]:
    return set(tokenize(text))


def build_index(documents: dict[str, str]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = defaultdict(set)
    for doc_id, text in documents.items():
        for term in unique_terms(text):
            index[term].add(doc_id)
    return dict(index)


def document_term_counts(text: str) -> Counter[str]:
    return Counter(tokenize(text))


def rank_documents(query_terms: list[str], documents: dict[str, str]) -> list[tuple[str, int]]:
    normalized_query = {term.lower() for term in query_terms}
    scores: list[tuple[str, int]] = []
    for doc_id, text in documents.items():
        counts = document_term_counts(text)
        score = sum(counts[term] for term in normalized_query)
        if score:
            scores.append((doc_id, score))
    return sorted(scores, key=lambda item: (-item[1], item[0]))


def summarize_collection_choice(values: list[str]) -> dict[str, object]:
    return {
        "ordered_values": list(values),
        "unique_values": set(values),
        "counts": Counter(values),
        "first_and_last": (values[0], values[-1]) if values else None,
    }
