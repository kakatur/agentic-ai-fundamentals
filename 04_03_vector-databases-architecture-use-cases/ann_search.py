"""Compare exact filtered search with FAISS HNSW and compute Recall@K."""

from __future__ import annotations

from dataclasses import dataclass

import faiss
import numpy as np


@dataclass(frozen=True)
class SearchComparison:
    exact_ids: tuple[str, ...]
    ann_ids: tuple[str, ...]
    recall: float


def recall_at_k(exact_ids: list[str] | tuple[str, ...], ann_ids: list[str] | tuple[str, ...]) -> float:
    """Return the fraction of exact top-K IDs also returned by ANN."""
    if not exact_ids:
        raise ValueError("exact results must not be empty")
    if len(set(exact_ids)) != len(exact_ids):
        raise ValueError("exact results must contain unique IDs")
    return len(set(exact_ids) & set(ann_ids)) / len(exact_ids)


class ProductHnswSearch:
    """A small static HNSW index per product to demonstrate filter parity."""

    def __init__(
        self,
        record_ids: list[str],
        products: list[str],
        vectors: np.ndarray,
        *,
        neighbors: int = 8,
        ef_search: int = 16,
    ) -> None:
        if len(record_ids) != len(products) or len(record_ids) != len(vectors):
            raise ValueError("IDs, products, and vectors must have equal lengths")
        if len(set(record_ids)) != len(record_ids):
            raise ValueError("record IDs must be unique")
        if not record_ids or vectors.ndim != 2 or vectors.shape[1] < 1:
            raise ValueError("at least one record with a nonempty vector is required")
        if neighbors < 2 or ef_search < 1:
            raise ValueError("neighbors must be at least 2 and ef_search must be positive")

        self._ids: dict[str, tuple[str, ...]] = {}
        self._vectors: dict[str, np.ndarray] = {}
        self._indexes: dict[str, faiss.IndexHNSWFlat] = {}
        self.ef_search = ef_search

        all_vectors = _normalize(vectors)
        product_values = sorted(set(products))
        for product in product_values:
            positions = [i for i, value in enumerate(products) if value == product]
            group_vectors = np.ascontiguousarray(all_vectors[positions], dtype="float32")
            index = faiss.IndexHNSWFlat(
                group_vectors.shape[1], neighbors, faiss.METRIC_INNER_PRODUCT
            )
            index.hnsw.efConstruction = max(40, ef_search)
            index.hnsw.efSearch = ef_search
            index.add(group_vectors)
            self._ids[product] = tuple(record_ids[i] for i in positions)
            self._vectors[product] = group_vectors
            self._indexes[product] = index

    def compare(
        self,
        query: np.ndarray,
        *,
        product: str,
        k: int = 5,
    ) -> SearchComparison:
        """Compare exact and ANN top-K over the same product-eligible set."""
        if product not in self._indexes:
            raise ValueError(f"unknown product: {product}")
        if k < 1:
            raise ValueError("k must be positive")

        vectors = self._vectors[product]
        ids = self._ids[product]
        if k > len(ids):
            raise ValueError("k cannot exceed the number of eligible records")
        normalized_query = _normalize(np.asarray(query, dtype="float32").reshape(1, -1))
        if normalized_query.shape[1] != vectors.shape[1]:
            raise ValueError("query dimension does not match the indexed vectors")

        exact_scores = vectors @ normalized_query[0]
        exact_positions = np.argsort(-exact_scores, kind="stable")[:k]
        exact_ids = tuple(ids[int(i)] for i in exact_positions)

        _scores, ann_positions = self._indexes[product].search(normalized_query, k)
        ann_ids = tuple(ids[int(i)] for i in ann_positions[0] if i >= 0)
        return SearchComparison(exact_ids, ann_ids, recall_at_k(exact_ids, ann_ids))


def _normalize(vectors: np.ndarray) -> np.ndarray:
    values = np.ascontiguousarray(vectors, dtype="float32")
    if not np.isfinite(values).all():
        raise ValueError("vectors must contain only finite values")
    norms = np.linalg.norm(values, axis=1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("vectors must be nonzero")
    return values / norms


def make_demo_search(*, count_per_product: int = 1200, dimension: int = 48) -> ProductHnswSearch:
    """Create a seeded synthetic corpus for a repeatable Recall@K example."""
    if count_per_product < 20 or dimension < 2:
        raise ValueError("demo needs at least 20 records per product and 2 dimensions")
    rng = np.random.default_rng(4307)
    products = ["iPhone App"] * count_per_product + ["Android App"] * count_per_product
    vectors = rng.normal(size=(len(products), dimension)).astype("float32")
    record_ids = [f"iphone-{i:04d}" for i in range(count_per_product)]
    record_ids.extend(f"android-{i:04d}" for i in range(count_per_product))
    return ProductHnswSearch(record_ids, products, vectors, neighbors=8, ef_search=12)


def demo_queries(*, count: int = 12, dimension: int = 48) -> np.ndarray:
    """Return deterministic query vectors independent of the indexed vectors."""
    rng = np.random.default_rng(4310)
    return rng.normal(size=(count, dimension)).astype("float32")
