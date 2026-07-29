# 04.03 - What Actually Happens Inside a Vector Database?

## Learning outcome

Trace a vector record through validation, storage, indexing, filtered search, update, and deletion; then decide when an exact or approximate index is justified.

## More than nearest neighbors

A vector database coordinates records, vectors, metadata, identity, filters, and an index. Useful behavior includes upsert, delete, version tracking, access-aware filtering, observable freshness, and ranked retrieval.

The teaching store uses exact search because it is transparent and provides ground truth. Approximate indexes such as HNSW and IVF trade some recall and operational complexity for lower query cost. Measure that trade against exact results.

## Lifecycle contract

1. Validate dimension and embedding version.
2. Upsert by stable record ID.
3. Update the searchable index.
4. Apply tenant and metadata eligibility before ranking.
5. Return score meaning and trace information.
6. Delete from both storage and search structures.

## Failure modes

- A successful write is temporarily invisible but freshness is undocumented.
- Post-search filtering removes all useful candidates or leaks unauthorized IDs.
- Re-embedding overwrites the rollback index.
- Deletion removes source text but leaves a searchable vector.
- Approximate recall is tuned without an exact baseline.

## Interview questions

### Basic

What does a vector index do? It organizes vectors so nearest-neighbor candidates can be found efficiently.

### Intermediate

Why filter before ranking? Eligibility is a security boundary, and post-filtering can distort both safety and relevance.

### Advanced

When should you adopt approximate search? When exact search misses a measured latency or throughput target and an evaluated index meets the required recall, freshness, memory, and update behavior.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
