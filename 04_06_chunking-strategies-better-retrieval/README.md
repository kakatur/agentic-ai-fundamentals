# 04.06 - Why Good Answers Disappear: Chunking for Better Retrieval

## Learning outcome

Implement fixed-window, overlapping, structure-aware, and parent-child chunking, then evaluate their boundaries using retrieval tasks.

## The answer exists, but no chunk contains it

A document can contain the exact answer and still fail retrieval. A fixed boundary may separate a heading from its explanation, split a procedure in half, or return the matching sentence without enough context to use it. The embedding model never gets a fair unit to represent.

To diagnose that failure, separate three jobs. The **search unit** receives an embedding and competes in ranking. The **context unit** is returned to the downstream model. The **evaluation unit** defines what counts as a complete answer. These units may differ.

Parent-child retrieval uses this separation directly: search a focused child chunk, then return a larger parent section that restores the surrounding explanation.

## Four strategies

### Fixed windows

Split every N words or tokens. Windows are deterministic, easy to batch, and useful as a baseline. They can separate a heading from its explanation or cut through a procedure.

### Overlapping windows

Repeat part of one window in the next. Overlap protects facts near boundaries and increases embedding count, storage, duplicate results, and context use. Measure that cost instead of choosing an arbitrary percentage.

### Structure-aware chunks

Follow headings, paragraphs, lists, tables, or code blocks. The source structure supplies meaningful boundaries, but noisy HTML and inconsistent markup must be cleaned first. Add size limits so one large section does not become an unbounded chunk.

### Parent-child chunks

Index smaller children and resolve selected results to larger parents. Preserve child ID, parent ID, source ID, and offsets. Deduplicate parents before building context when several children point to the same section.

## Preserve traceability

[`chunking.py`](chunking.py) records stable IDs and word offsets. A useful chunk record also carries source revision, chunker version, heading path, and content hash. Those fields let you inspect a match, rebuild the corpus, and distinguish current from stale chunks.

## Evaluate dangerous boundaries

Create test queries for:

- an answer separated from its heading;
- a numbered procedure crossing a window;
- a table row separated from its header;
- code separated from the explanation;
- several matching children under one parent.

Measure retrieval recall, answer completeness, duplicate rate, context tokens, latency, and index size. Compare the full retrieval-and-answer pipeline because a precise small chunk can retrieve well while returning too little context.

## Migration rule

A chunking change creates a new corpus. Build a separately versioned index from original documents, replay the same evaluation set, inspect changed failures, and shift traffic with rollback. Do not mix chunks produced by incompatible policies in one unexplained index.

## Interview questions

### Basic

**Why avoid one vector for a long document?** Unrelated topics compete inside one representation, and returned context may exceed the useful budget.

### Intermediate

**What does overlap trade?** Better boundary coverage for more embeddings, storage, duplicates, and context use.

### Advanced

**How do you select a strategy?** Match document structure and answer scope, test boundary-sensitive queries, measure retrieval and downstream completeness, and version every corpus change.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
