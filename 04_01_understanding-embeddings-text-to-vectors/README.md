# 04.01 - How Semantic Search Understands What Keywords Can't

## Learning outcome

Build a small deterministic embedding pipeline, explain what an embedding can and cannot represent, and recognize when two vectors are unsafe to compare.

## Start with the problem

A user searches for "change my login secret" while the help center says "reset your password." Keyword overlap is weak even though the intent is close. An embedding model maps each text into a fixed-length vector so a retrieval system can compare positions rather than exact words.

The coordinates are not human-readable labels. Their value comes from relationships learned by the model: related inputs tend to occupy nearby regions in the model's vector space.

## The embedding contract

An embedding pipeline must keep four things explicit:

1. **Model and version** — changing either may change the coordinate system.
2. **Input preparation** — prefixes, truncation, and normalization affect output.
3. **Dimension** — every vector in one index must have the expected length.
4. **Similarity policy** — the metric and any vector normalization must match ingestion and query time.

Equal dimensions do not prove compatibility. Two unrelated models can both emit 384 numbers while assigning completely different meaning to each direction.

## Demo design

The lesson uses a deterministic token-hashing embedder. It is intentionally not a semantic model. That limitation is useful: the code demonstrates dimension, repeatability, normalization, and versioning without pretending that token hashing understands synonyms.

## Failure modes and decisions

- Reject dimension mismatches instead of padding or trimming vectors.
- Define a policy for empty input and zero vectors.
- Version the embedding configuration with the index.
- Re-embed into a separate index when changing models.
- Evaluate a real model with labeled queries, paraphrases, and hard negatives.

## Interview questions

### Basic

What is an embedding? A fixed-length numerical representation whose relative position can encode useful relationships between inputs.

### Intermediate

Why can two vectors with the same dimension still be incompatible? Dimension describes shape, not the coordinate system learned by the model.

### Advanced

How would you migrate embedding models safely? Build a separately versioned index, replay labeled evaluation queries, compare quality and latency, shift traffic gradually, and retain rollback.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
