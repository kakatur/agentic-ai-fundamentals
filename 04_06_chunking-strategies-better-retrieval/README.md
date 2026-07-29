# 04.06 - Bad Chunking Is Quietly Ruining Your RAG Results

## Learning outcome

Implement fixed, overlapping, structure-aware, and parent-child chunking; preserve source traceability; and evaluate boundaries with retrieval tasks rather than intuition.

## Three different units

The **search unit** receives an embedding and competes in ranking. The **context unit** is sent downstream. The **evaluation unit** defines what counts as a useful result. They do not always need the same size.

Fixed windows are predictable but can cut through meaning. Overlap protects boundaries at the cost of duplicate storage and results. Structure-aware splitting respects headings and paragraphs. Parent-child retrieval searches a focused child and returns a larger parent for context.

## Evaluation

Create queries whose answers cross headings, list boundaries, and window edges. Measure retrieval recall, answer completeness, duplicate pressure, context tokens, and latency. Version the chunker and preserve original documents, offsets, and parent IDs so the corpus can be rebuilt.

## Interview questions

### Basic

Why not put a whole document in one chunk? One vector can blur unrelated topics, while the returned context may exceed the useful budget.

### Intermediate

What does overlap trade? Better boundary coverage for more embeddings, storage, and near-duplicate candidates.

### Advanced

How do you migrate chunking strategies? Build a separately versioned index, evaluate boundary-sensitive queries and answer completeness, inspect cost and duplication, then shift traffic with rollback.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
