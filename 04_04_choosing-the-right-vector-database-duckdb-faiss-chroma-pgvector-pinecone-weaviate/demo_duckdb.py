"""Run DuckDB search over the help-center articles."""

from __future__ import annotations

import duckdb
from local_backends import SearchRecord
from article_data import load_records, QUERY, QUERY_VECTOR, PRODUCT_FILTER


def search_with_duckdb(records: list[SearchRecord]) -> list[tuple[str, str, float]]:
    connection = duckdb.connect(database=":memory:")
    connection.execute("""
        CREATE TABLE articles (
            article_id VARCHAR,
            name VARCHAR,
            product VARCHAR,
            document VARCHAR,
            embedding FLOAT[]
        )
    """)
    rows = [
        (record.record_id, record.name, record.metadata["product"],
         record.document, list(record.embedding))
        for record in records
    ]
    connection.executemany("INSERT INTO articles VALUES (?, ?, ?, ?, ?)", rows)
    return connection.execute("""
        SELECT article_id, name,
               list_cosine_distance(embedding, ?::FLOAT[]) AS cosine_distance
        FROM articles
        WHERE product = ?
        ORDER BY cosine_distance, article_id
        LIMIT 3
    """, [list(QUERY_VECTOR), PRODUCT_FILTER["product"]]).fetchall()


def main() -> None:
    records = load_records()
    print(f'Question: "{QUERY}"  |  product filter: billing')
    print("DuckDB exact cosine search:")
    for article_id, name, distance in search_with_duckdb(records):
        print(f"  {article_id}: {name} (cosine distance={distance:.3f})")


if __name__ == "__main__":
    main()
