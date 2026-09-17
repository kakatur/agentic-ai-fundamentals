from vector_store import ExactVectorStore, Record


store = ExactVectorStore(dimension=2, embedding_version="embed-v1")
store.upsert(Record("reset", "Reset your password", (1.0, 0.0), "acme", "embed-v1", {"team": "support"}))
store.upsert(Record("invoice", "Download an invoice", (0.0, 1.0), "acme", "embed-v1", {"team": "billing"}))
store.upsert(Record("private", "Another tenant", (1.0, 0.0), "other", "embed-v1"))

for hit in store.query((0.9, 0.1), tenant_id="acme", metadata_filter={"team": "support"}):
    print(f"{hit.score:.3f}  {hit.record_id}  {hit.text}")
