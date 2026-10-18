# 4.3 — Vector Search Masterclass: Filtering, Lifecycle, and Recall

## Learning outcome

Compare filtered approximate-nearest-neighbor results with an exact baseline using Recall@K, while tracing the record identity and lifecycle that make results safe to use.

## Start with a record

A searchable record needs an ID, source text or a source reference, an embedding version, and filterable metadata. This lesson traces those data elements and then compares exact and approximate retrieval under the same eligibility rule.

A useful search record therefore has more than a vector:

| Field | Why it matters |
|---|---|
| ID | Connects updates, search results, and deletion to the same source item |
| Source text or source reference | Lets the application show or retrieve the content behind a match |
| Embedding and embedding version | Defines the vector's coordinates and the model that produced them |
| Filterable metadata | Defines tenant, permissions, document type, and other eligibility rules |
| Optional source revision | Identifies the source version associated with the record |

The searchable index is derived from these records. Keep the source of truth and the index connected by IDs and explicit versions.

## Follow one support article

Suppose a help center contains article `iphone-reset-17`, for the iPhone App, with source revision `12`. Its embedding comes from model configuration `embed-v3`. An iPhone App user asks how to regain account access.

In production, ingestion should validate the embedding dimension and model version. In this lesson, `ExactVectorStore` checks that a record's version tag matches its configured expected version; it does not verify which model produced the vector. The FAISS recall demo uses synthetic vectors with no model-version metadata. Eligibility determines which records may appear in results. In this demo, the query applies the product rule and returns the record ID and source text. In production, a system may return a source reference that the application uses to fetch the content.

Now the article changes. An upsert with the same ID should replace revision `12` with revision `13`; the revision may be stored with the searchable record or maintained by the source system. If the model changes too, store the new model version explicitly and rebuild or migrate the affected vectors. Finally, a deletion must remove the record from every searchable path the application can query.

A search has two separate parts: eligibility determines which records may appear, and retrieval determines how the system finds and ranks matches. ANN systems may restrict search to eligible records, guide index traversal, or filter retrieved candidates afterward. Post-filtering a limited candidate set can return fewer eligible results than requested.

```text
eligibility -> records permitted to appear in results
retrieval   -> exact scoring or ANN candidate search
ANN filters -> restrict eligible set / guide traversal / filter candidates
result      -> eligible ranked records + source text (demo) or source reference (production)
```

## A runnable exact and ANN comparison

The repository includes an exact lifecycle baseline in `vector_store.py` and an approximate-search comparison in `ann_search.py`. The `VectorRecord` dataclass groups an ID, product, source text, embedding, and embedding version. The `ExactVectorStore` class stores records by ID, filters by product before cosine ranking, replaces a record on upsert, and removes it on deletion. The ANN example uses FAISS HNSW with normalized vectors and a separate index per product so exact and approximate search see the same eligible set.

Run the example from this lesson directory:

```bash
python3 -m pip install -r requirements.txt
python3 demo.py
python3 -m unittest -v
```

The lifecycle store is an in-memory exact-search baseline. The HNSW example is also an in-memory teaching setup; it demonstrates ANN retrieval and recall measurement, not production-scale performance or a universal way to implement metadata filters.

The deletion demonstrated by `demo.py` applies only to `ExactVectorStore`; it does not modify the separate FAISS HNSW index. FAISS HNSW does not support removing vectors in place. A deployed system using HNSW must rebuild and replace the index or use an index/backend whose deletion behavior meets the application's requirements. Keep deletion consistent across every search path.

## Eligibility and retrieval are separate parts

Authorization and metadata define which records are eligible to appear. Retrieval and ranking determine which matches the system finds and orders. Keep those concerns separate even when a particular exact-search implementation applies its product filter before scoring.

ANN filter execution depends on the system. It can limit search to eligible records, guide index traversal, or filter retrieved candidates afterward. With post-filtering, a limited candidate set may contain too few eligible records to fill the requested result count. The FAISS demo uses per-product indexes to hold the eligible set constant; deployed systems may provide native filter support or need another design. Test the actual production filter conditions.

## Exact search is a useful baseline

Exact search scores every eligible vector and provides a correctness baseline, though cost grows with the eligible set. ANN indexes explore a limited portion of an index and can trade recall for search work and memory. Their filtering behavior and tuning controls depend on the implementation.

The demo compares exact and ANN top-K IDs under the same query, product filter, and cosine metric. Recall@K measures the fraction of exact top-K IDs also found by ANN:

```text
Recall@K = |exact_top_k ∩ ann_top_k| / |exact_top_k|
```

It prints the first query's exact and ANN IDs, its Recall@5, and the mean across a seeded set of synthetic queries. The demo uses seeded random vectors, so these recall results illustrate the calculation; they do not evaluate semantic relevance or application search quality. FAISS HNSW's `efSearch` controls search exploration and can change the speed-accuracy trade-off. Choose settings with representative data and queries, and measure latency as well as recall.

## Diagnose the failed result

When `iphone-reset-17` is missing, inspect the stages in order:

1. Was the record written with the expected ID, revision, and model version?
2. Was it eligible under this caller's product and permission filters?
3. Did the record appear among the ANN results returned to the application? Compare the returned IDs with the exact top-K results and measure Recall@K.
4. If the application reranked or truncated the results, did that step move the record below the requested result count?
5. Did the returned ID resolve to the current source revision?

This order distinguishes a data or access bug from an index-recall or ranking problem. Changing similarity settings will not repair a stale source reference or a missing product filter.

## Trade-offs and failure conditions

A dedicated vector database can provide persistence, metadata filtering, and index management, but it introduces another operational boundary. A relational database with a vector extension or a local index may be simpler when existing storage and traffic fit. The right choice depends on lifecycle, consistency, filtering, scale, and operational requirements; embeddings alone do not determine it.

Treat embedding-model or chunking changes as index migrations. Keep source records, build the new version separately, compare it on a fixed evaluation set, then switch reads with a rollback path. Mixing vectors from incompatible model versions in one search space can make scores meaningless.

## Interview questions

### Basic

**What does a vector database store besides embeddings?**

A searchable record usually needs an ID, an embedding, source text or a reference, filterable metadata, and enough version information to manage updates and rebuilds.

### Intermediate

**Why should eligibility be separate from similarity ranking?**

Eligibility enforces product and permission rules. Ranking orders only the records the caller may see. Mixing the stages can return ineligible results or remove useful candidates after a limited approximate search.

### Advanced

**How would you investigate a missing result?**

Check ingestion and version state, eligibility filters, whether the record appears in ANN’s returned IDs, any later reranking or result limit, then source resolution. Compare ANN results with exact search to isolate recall loss.

## References

- FAISS index types, HNSW parameters, and cosine search with normalized inner product — https://github.com/facebookresearch/faiss/wiki/Faiss-indexes
- FAISS index selection guidance and HNSW limitations — https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index
- Qdrant filtered-search strategies — https://qdrant.tech/documentation/search-patterns/vector-search-filtering/

Documentation checked: 2026-10-17. Recheck version-sensitive implementation details before recording.
