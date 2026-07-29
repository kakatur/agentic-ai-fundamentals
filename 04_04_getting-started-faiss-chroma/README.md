# 04.04 - FAISS or Chroma? Build Local Vector Search the Right Way

## Learning outcome

Choose the right local abstraction, prepare vectors safely for FAISS, and keep a stable record contract when using a Chroma collection.

## Different responsibilities

FAISS is an efficient similarity-search library built around indexes. Chroma's collection primitive stores and queries embeddings alongside IDs, documents, and metadata. They overlap at nearest-neighbor search but expose different application responsibilities.

This lesson keeps vendor imports inside adapter functions and tests the request boundary with fakes. Install optional packages only when running a real backend.

## FAISS path

- Convert vectors to a rectangular NumPy float32 matrix.
- Choose an index and metric intentionally.
- Normalize indexed and query vectors when mapping cosine similarity to inner product.
- Preserve stable IDs outside a flat index or use an ID-mapping wrapper.

## Chroma path

- Create or retrieve a named collection.
- Decide whether Chroma or the application owns embedding generation.
- Upsert aligned IDs, documents, embeddings, and metadata.
- Use metadata filters as part of the query contract.

## Interview questions

### Basic

What is the main difference? FAISS centers on vector indexes; Chroma centers on collections of records and embeddings.

### Intermediate

Why pass embeddings explicitly in this lesson? It keeps the embedding model and version visible at the application boundary.

### Advanced

How would you keep the backend replaceable? Own stable record IDs, embedding configuration, evaluation queries, and a narrow adapter contract outside either SDK.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```

Optional real backends: `numpy`, `faiss-cpu`, and `chromadb`.
