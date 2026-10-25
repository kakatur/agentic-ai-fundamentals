"""Shared article loading and query inputs for the backend demos."""

from __future__ import annotations

import json
from pathlib import Path

from local_backends import SearchRecord


LESSON_DIR = Path(__file__).resolve().parent
ARTICLES_DIR = LESSON_DIR / "help_center"
VECTOR_FILE = ARTICLES_DIR / "article_vectors.jsonl"
QUERY = "Why was I charged twice?"
QUERY_VECTOR = (1.0, 0.0, 0.0)  # Example vector, not a model embedding.
PRODUCT_FILTER = {"product": "billing"}


def load_records() -> list[SearchRecord]:
    articles = []
    with VECTOR_FILE.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            try:
                article = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{VECTOR_FILE.name}:{line_number}: invalid JSON") from error
            if not isinstance(article, dict):
                raise ValueError(f"{VECTOR_FILE.name}:{line_number}: expected an article object")
            articles.append(article)
    records = []
    seen_ids = set()
    for article in articles:
        article_id = article["id"]
        name = article["name"]
        if article_id in seen_ids:
            raise ValueError("article IDs must be unique")
        seen_ids.add(article_id)
        path = ARTICLES_DIR / f"{article_id}.md"
        records.append(SearchRecord(
            record_id=article_id,
            name=name,
            document=path.read_text(encoding="utf-8").strip(),
            embedding=tuple(article["embedding"]),
            metadata={"product": article["product"], "source": str(path.relative_to(LESSON_DIR))},
            embedding_version="embed-v1",
        ))
    return records
