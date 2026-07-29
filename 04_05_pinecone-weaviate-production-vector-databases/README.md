# 04.05 - Pinecone or Weaviate? Choose With Evidence, Not Hype

## Learning outcome

Turn a workload into a reproducible database evaluation instead of choosing Pinecone or Weaviate from a generic feature checklist.

## Workload before vendor

Record vector count and dimension, growth, query and write rates, burst shape, filter selectivity, tenant boundaries, freshness, durability, regions, recovery objectives, and team ownership. Then run the same labeled workload against every candidate.

Pinecone is a managed service whose current indexes can support dense, sparse, and evolving document-oriented search capabilities. Weaviate offers managed and self-hosted deployment choices, collections, vector and inverted indexes, hybrid retrieval, and several vector-index types. These capabilities change; verify current documentation at decision time.

## Evaluation plan

- Use identical vectors, labeled queries, metadata, and concurrency.
- Measure recall or ranking quality, p50/p95/p99 latency, ingestion rate, freshness, and filtered behavior.
- Exercise update, delete, backup, restore, and re-embedding workflows.
- Estimate total cost with a dated workload and explicit assumptions.
- Preserve source records, stable IDs, evaluation sets, and an export path.

## Interview questions

### Basic

What should you compare first? Your workload and operating requirements, not vendor logos.

### Intermediate

Why test filtered queries separately? Filter selectivity changes candidate work and may expose different latency or recall behavior.

### Advanced

What makes a vendor decision revisitable? A dated benchmark, explicit assumptions, portable source data, stable IDs, versioned embeddings, and a tested exit path.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```

Verify current capabilities in the official Pinecone and Weaviate documentation before implementation.
