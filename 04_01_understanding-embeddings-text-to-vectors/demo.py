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


def main() -> None:
    model = load_model()
    query = embed_texts(model, [QUERY], role="query")[0]
    documents = embed_texts(model, DOCUMENTS, role="document")

    print(f"model: {MODEL_ID}")
    print(f"revision: {MODEL_REVISION[:12]}")
    print(f"expected dimension: {EMBEDDING_DIMENSION}")
    print(f"actual dimension: {len(query.values)}")
    print(f"query: {QUERY!r}\n")
    print("keyword overlap:")
    for document in documents:
        overlap = sorted(exact_token_overlap(QUERY, document.text))
        print(f"  {str(overlap):12} {document.text}")

    print("\nembedding ranking:")
    for score, document in rank_documents(query, documents):
        print(f"  {score:+.3f}       {document.text}")


if __name__ == "__main__":
    main()
