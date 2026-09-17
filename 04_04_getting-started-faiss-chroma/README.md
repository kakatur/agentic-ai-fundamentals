# 04.04 - FAISS vs Chroma: What Your Application Must Own

## Learning outcome

Build the same record boundary around FAISS and Chroma, prepare vectors correctly for each path, and identify which responsibilities remain in the application.

## The first query works. What did the tool actually solve?

FAISS and Chroma can both return a convincing nearest result from a tiny local demo. That success hides an important difference: FAISS centers on a vector index, while Chroma exposes a collection that can keep IDs, documents, embeddings, and metadata together. They solve different portions of the application.

The useful comparison is therefore not "Which tool is better?" It is "Which responsibilities does this tool accept, and which ones still belong to my code?"

Keep this application-owned record at the boundary:

```text
stable ID + source document + embedding + metadata + embedding version
```

This contract keeps ingestion testable and makes a later backend change a replay from source records instead of a data rescue.

## FAISS path

1. Validate nonempty, equal-dimension embeddings and unique record IDs.
2. Convert the batch to a rectangular NumPy `float32` matrix.
3. Select an index and metric explicitly.
4. Add the vectors and preserve a mapping from FAISS labels to stable record IDs.
5. Apply the identical preprocessing to query vectors.

`IndexFlatL2` performs exact search and returns squared L2 distances. `IndexFlatIP` performs maximum inner-product search. For cosine similarity, normalize stored and query vectors before using inner product. Flat indexes use sequential positions unless wrapped with an ID-mapping index.

Start with a flat index as a baseline. Move to an approximate index only after the exact path misses a measured target.

## Chroma path

A collection can accept aligned sequences of IDs, documents, embeddings, and metadata. Chroma can generate embeddings through a configured embedding function, or the application can supply them.

This lesson supplies embeddings so the model contract remains explicit. If the collection owns embedding, pin and record that configuration with the collection. Query dimensions must match the collection's existing embeddings.

Use `upsert` when rerunning ingestion should replace records with the same ID. Add metadata filters to integration tests whenever they affect access or product behavior.

## Testing the boundary

Unit tests can validate record alignment and the payload sent to an SDK without installing optional packages. They cannot verify a vendor's indexing, persistence, or filter semantics. Add a small pinned integration suite for those behaviors.

Use a dataset small enough to inspect:

- one result with an obvious nearest vector;
- one duplicate ID that must fail or replace deliberately;
- one metadata filter;
- one update and one delete;
- one restart if persistence matters.

## Decision guide

Choose FAISS when you want direct index control and can own records, metadata, persistence, and ID mapping elsewhere. Choose Chroma when a collection-level record API and its query features fit the application. In both cases, retain source records, stable IDs, configuration versions, and labeled queries outside the backend.

## Current documentation checked

- [FAISS metrics and cosine mapping](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances)
- [FAISS index behavior and ID mapping](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)
- [Chroma collections](https://docs.trychroma.com/docs/collections/manage-collections)
- [Chroma query and filters](https://docs.trychroma.com/docs/querying-collections/query-and-get)

Retrieved September 8, 2026. Recheck SDK signatures before implementation.

## Interview questions

### Basic

**What is the main difference?** FAISS centers on vector indexes; Chroma centers on collections of records and embeddings.

### Intermediate

**Why use explicit embeddings here?** It keeps model ownership, versioning, and migration visible at the application boundary.

### Advanced

**How do you keep the backend replaceable?** Own stable records, embedding configuration, evaluation data, and a narrow adapter; rebuild backend indexes from those assets.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```

Install `numpy` and `faiss-cpu` for the real FAISS adapter, or `chromadb` for a Chroma integration test.
