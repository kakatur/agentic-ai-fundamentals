from embeddings import (
    EMBEDDING_DIMENSION,
    MODEL_ID,
    MODEL_REVISION,
    embed_texts,
    exact_token_overlap,
    load_model,
    rank_documents,
)


QUERY = "I can't log in"
DOCUMENTS = [
    "Reset your password to regain account access.",
    "Download last quarter's revenue report.",
    "Track a package that is out for delivery.",
]


def build_in_memory_index(model):
    """Encode the fixed demo corpus once for this program run."""
    return embed_texts(model, DOCUMENTS, role="document")


def search(model, query_text, document_index):
    """Encode one query and compare it with the in-memory document vectors."""
    query = embed_texts(model, [query_text], role="query")[0]
    return query, rank_documents(query, document_index)


def main() -> None:
    model = load_model()
    print("building in-memory document index...")
    document_index = build_in_memory_index(model)
    print(f"indexed documents: {len(document_index)}")

    query, results = search(model, QUERY, document_index)

    print(f"model: {MODEL_ID}")
    print(f"revision: {MODEL_REVISION[:12]}")
    print(f"expected dimension: {EMBEDDING_DIMENSION}")
    print(f"actual dimension: {len(query.values)}")
    print(f"query: {QUERY!r}\n")
    print("keyword overlap:")
    for document in document_index:
        overlap = sorted(exact_token_overlap(QUERY, document.text))
        print(f"  {str(overlap):12} {document.text}")

    print("\nembedding ranking:")
    for score, document in results:
        print(f"  {score:+.3f}       {document.text}")

    print("\nThe in-memory index is rebuilt each time this script runs.")


if __name__ == "__main__":
    main()
