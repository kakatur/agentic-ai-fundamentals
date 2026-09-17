# 04.03 - Inside a Vector Database: Records, Indexes, and Search

## Learning outcome

Trace a vector record through validation, storage, filtering, ranking, update, and deletion; then decide when approximate search is justified.

## Start with the record

A nearest-neighbor function can rank a few vectors. A searchable application has a harder promise to keep: the right record must be searchable, visible only to the right caller, replaceable without leaving an old copy behind, and removable everywhere.

That is why a vector database manages more than vectors. A useful record contains a stable ID, source text or a source reference, an embedding, filterable metadata, and the version of the embedding configuration. Follow that record through the system and the architecture becomes easier to reason about.

```text
source -> embed -> validate -> store record -> update index
query  -> embed -> apply eligibility -> find candidates -> rank -> fetch
```

The stable ID connects both paths. It makes an upsert replace the intended record, lets a result resolve back to its source, and gives deletion an exact target.

## The write path

Validate dimension and embedding version before changing storage. Store the record under a stable ID, then make its vector searchable. The API should state when a successful write becomes visible to queries. That distinction matters when indexing is asynchronous.

Treat re-embedding as a migration. Write new vectors into a separate versioned index, evaluate them, shift reads, and retain rollback until the old index can be removed safely.

## The query path

Query processing has two different jobs:

1. **Eligibility** decides which records the caller may search using tenant, permission, time, or metadata rules.
2. **Ranking** orders the eligible candidates using vector distance or similarity.

Apply authorization consistently to every retrieval path. Post-filtering a small nearest-neighbor list can also remove all useful candidates, so test filtered recall separately from unfiltered recall.

## Exact and approximate indexes

Exact search compares the query with every eligible vector. It is easy to reason about and provides a correctness baseline.

Approximate nearest-neighbor indexes reduce search work. HNSW navigates a graph; IVF first narrows the search to selected partitions. Their parameters affect build time, memory, query latency, and recall.

Adopt approximation when exact search misses a measured latency or throughput target. Compare approximate results with exact top-k results, then tune until recall and operational costs meet the application requirement.

## Lifecycle tests

The lesson's [`ExactVectorStore`](vector_store.py) deliberately uses exact search so every stage is visible. Its tests verify:

- dimension and embedding-version validation;
- upsert replacement under a stable ID;
- tenant and metadata eligibility before ranking;
- deterministic ordering for tied scores;
- deletion from the searchable record set.

When evaluating a database, extend this sequence with freshness timing, concurrent writes, backup and restore, and a full rebuild from source data.

## Diagnostic trace

For a failed query, capture the index version, embedding version, filter policy, eligible count, candidate count, metric, and returned IDs. This separates a missing record into three questions: Was it eligible? Did the index retrieve it? Did ranking place it high enough?

## Interview questions

### Basic

**What does a vector index do?** It organizes vectors so a query can find nearby candidates efficiently.

### Intermediate

**Why keep exact search?** It provides ground truth for measuring approximate recall and diagnosing ranking changes.

### Advanced

**When do you need a dedicated vector database?** When its record lifecycle, filtering, isolation, scale, availability, and operational model fit measured requirements better than a local index or an existing database with vector support.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
