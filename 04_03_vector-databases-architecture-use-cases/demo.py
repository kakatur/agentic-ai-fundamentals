"""Compare filtered exact and ANN search, then demonstrate record lifecycle."""

from ann_search import demo_queries, make_demo_search

from vector_store import ExactVectorStore, VectorRecord


search = make_demo_search()
queries = demo_queries()
comparisons = [search.compare(query, product="iPhone App", k=5) for query in queries]
mean_recall = sum(result.recall for result in comparisons) / len(comparisons)
print("Filtered exact vs. FAISS HNSW (iPhone App, Recall@5):")
print("  exact top 5:", ", ".join(comparisons[0].exact_ids))
print("  ANN top 5:  ", ", ".join(comparisons[0].ann_ids))
print(f"  first-query Recall@5: {comparisons[0].recall:.2f}")
print(f"  mean Recall@5 across {len(comparisons)} queries: {mean_recall:.2f}")

store = ExactVectorStore(dimension=2, expected_embedding_version="demo-v1")
# Source revisions can live beside the source system rather than in VectorRecord.
source_revisions = {"iphone-reset-17": 12}
store.upsert(
    VectorRecord(
        record_id="iphone-reset-17",
        product="iPhone App",
        text="Reset your password to regain account access.",
        embedding=(0.98, 0.20),
        embedding_version="demo-v1",
    )
)
store.upsert(
    VectorRecord(
        record_id="revenue-4",
        product="iPhone App",
        text="Quarterly revenue increased by four percent.",
        embedding=(0.05, 0.99),
        embedding_version="demo-v1",
    )
)
store.upsert(
    VectorRecord(
        record_id="android-reset-2",
        product="Android App",
        text="Android App password-reset guide.",
        embedding=(1.0, 0.0),
        embedding_version="demo-v1",
    )
)

query = (1.0, 0.0)
print("iPhone App search:")
for record, score in store.search(query, product="iPhone App"):
    print(f"  {record.record_id}: {score:.3f} — {record.text}")

print(f"\nReplace iphone-reset-17 revision {source_revisions['iphone-reset-17']} with revision 13:")
store.upsert(
    VectorRecord(
        record_id="iphone-reset-17",
        product="iPhone App",
        text="Use the account recovery page to reset your password.",
        embedding=(0.96, 0.28),
        embedding_version="demo-v1",
    )
)
source_revisions["iphone-reset-17"] = 13
print(f"  source revision: {source_revisions['iphone-reset-17']}")
print("  ", store.search(query, product="iPhone App")[0][0].text)

print("\nDelete iphone-reset-17:")
store.delete("iphone-reset-17")
print("  remaining iPhone App IDs:", [r.record_id for r, _ in store.search(query, product="iPhone App")])
