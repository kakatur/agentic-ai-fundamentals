# 04.05 - How to Evaluate Pinecone and Weaviate for Your Workload

## Learning outcome

Turn application requirements into a reproducible vector-database evaluation that covers retrieval quality, filtered latency, freshness, lifecycle behavior, cost, and team ownership.

## Write the workload first

A feature table can make two vector databases look directly comparable. It says both products support vectors, filters, scaling, and hybrid retrieval, so the decision appears to be a matter of checking boxes. The first realistic workload usually breaks that illusion.

Describe the system before comparing products:

- vector count, dimension, growth, retention, and metadata size;
- queries and writes per second, burst shape, and concurrency;
- filter frequency and selectivity, tenant count, and isolation needs;
- freshness, availability, regions, backup, restore, and recovery objectives;
- team capacity for upgrades, monitoring, security, and incidents.

A benchmark result is meaningful only for the workload that produced it. The evaluation starts with the workload because the winner can change with filter selectivity, freshness targets, regions, growth, and the operational work your team is prepared to own.

## Compare operating models

Pinecone provides a managed service. Weaviate provides managed and self-hosted options. That difference changes which operational work the team owns, but the application still owns data quality, embedding migrations, retrieval evaluation, and access rules.

Current capabilities evolve. Pinecone documents dense and sparse records, namespaces, and metadata filtering. Weaviate documents collections with vector and inverted indexes, filtered vector search, and hybrid retrieval. Verify the exact API version and deployment option during the evaluation.

## Build a fair benchmark

Load identical vectors, IDs, metadata, and labeled queries. Warm-up policy, concurrency, region, client settings, and filters must also match. Measure:

- recall@k or a task-appropriate ranking metric;
- p50, p95, and p99 latency by query slice;
- ingestion throughput and time until a write is searchable;
- error and retry behavior under bursts;
- update, delete, backup, restore, export, and rebuild behavior.

Filtered queries deserve separate slices because selectivity changes the candidate set and can change both latency and recall.

## Use gates before preferences

[`evaluation.py`](evaluation.py) checks measured results against minimum recall, maximum p95 latency, freshness, and cost. A candidate passes only when every required gate passes. Keep optional preferences in a separate scorecard so a convenient feature cannot hide a failed correctness requirement.

Run expected and growth scenarios. Record the date, data size, traffic, storage, replicas, regions, discounts, and staffing assumptions behind cost estimates.

## Preserve the exit path

Keep original documents, stable IDs, embeddings or a reproducible embedding job, versioned schemas, labeled queries, and an export test. A decision record should include assumptions, evidence, rejected options, known risks, and retest triggers such as three-times growth or a new region.

## Current documentation checked

- [Pinecone metadata filtering](https://docs.pinecone.io/guides/search/filter-by-metadata)
- [Pinecone index creation](https://docs.pinecone.io/guides/index-data/create-an-index)
- [Weaviate indexing](https://docs.weaviate.io/weaviate/concepts/indexing)
- [Weaviate filtered vector search](https://docs.weaviate.io/weaviate/concepts/filtering)

Retrieved September 8, 2026. Treat product capabilities, limits, and pricing as volatile.

## Interview questions

### Basic

**What should you define before comparing databases?** The workload, correctness requirements, operating constraints, and ownership model.

### Intermediate

**Why measure filtered queries separately?** Filter selectivity changes candidate work and may expose different latency or recall behavior.

### Advanced

**What makes the decision revisitable?** Dated inputs, repeatable benchmarks, portable data, versioned configurations, and explicit retest triggers.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
