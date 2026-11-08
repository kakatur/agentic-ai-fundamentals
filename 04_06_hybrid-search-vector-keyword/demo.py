"""Build a small support corpus and compare retrieval rankings."""
from sentence_transformers import SentenceTransformer
from hybrid import MODEL, build, connect, search

DOCUMENTS = [
    ("reset", "support", "Account recovery: reset your password using the link in the email."),
    ("e104", "support", "Error E104: the password reset token has expired. Request a new reset link."),
    ("e105", "support", "Error E105: your account is temporarily locked after too many login attempts."),
    ("mfa", "support", "Replace a lost authentication device using your backup recovery codes."),
    ("billing", "support", "Update the credit card used for your monthly subscription."),
    ("private", "internal", "Error E104 internal investigation notes for administrators."),
]
QUERIES = ["My password reset link doesn't work", "E104", "E104 password reset link expired"]


def main():
    model = SentenceTransformer(MODEL)
    db = connect(":memory:")
    build(db, DOCUMENTS, model.encode([d[2] for d in DOCUMENTS]))
    for query in QUERIES:
        query_embedding = model.encode(query)
        dense, lexical, fused = search(db, query, query_embedding, "support")
        print(f"\nQuery: {query}\n  vector: {dense}\n  keyword: {lexical}\n  fused: {fused}")
    db.close()


if __name__ == "__main__":
    main()
