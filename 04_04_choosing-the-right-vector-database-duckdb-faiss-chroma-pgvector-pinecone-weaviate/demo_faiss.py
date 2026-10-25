"""Run FAISS search over the help-center articles."""

from __future__ import annotations

from local_backends import FaissAdapter
from local_backends import SearchRecord
from article_data import load_records, QUERY, QUERY_VECTOR, PRODUCT_FILTER


def search_with_faiss(records: list[SearchRecord]) -> list[tuple[str, str, float]]:
    store = FaissAdapter(dimension=len(QUERY_VECTOR))
    for record in records:
        store.upsert(record)
    hits = store.search(QUERY_VECTOR, filters=PRODUCT_FILTER, limit=3)
    return [(hit.record_id, hit.name, hit.score) for hit in hits]


def main() -> None:
    records = load_records()
    print(f'Question: "{QUERY}"  |  product filter: billing')
    print("FAISS flat-index search:")
    for article_id, name, distance in search_with_faiss(records):
        print(f"  {article_id}: {name} (squared L2 distance={distance:.3f})")


if __name__ == "__main__":
    main()
