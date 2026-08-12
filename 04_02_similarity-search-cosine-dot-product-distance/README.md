# 04.02 - Measuring Vector Similarity: Cosine, Dot Product, and Euclidean Distance

## Learning outcome

Explain what cosine similarity, dot product, and Euclidean distance measure; implement each one; and choose a metric and ranking direction that match an embedding model's guidance.

## From embeddings to search

Lesson 4.1 turned text into vectors in a shared vector space. Search adds one more operation: compare the query vector with each document vector and rank the results.

The comparison rule is called a **comparison metric**. Different metrics focus on different geometric relationships, so this lesson introduces them one at a time before comparing their rankings.

The examples use this query vector:

```text
query = [1.0, 0.0]
```

## Cosine similarity: compare direction

Cosine similarity compares the angle between two vectors. Vector length is divided out, so vectors pointing in the same direction receive the same cosine score even when one is longer.

```text
cosine([1, 0], [4, 0]) = 1.0
```

A score near `1` means similar direction, `0` means perpendicular directions, and `-1` means opposite directions. Larger scores rank first.

## Dot product: compare alignment and magnitude

The dot product multiplies matching coordinates and adds the results. It rewards aligned vectors, but unlike cosine similarity, it keeps magnitude in the score.

```text
dot([1, 0], [4, 0]) = (1 × 4) + (0 × 0) = 4.0
```

A longer aligned vector can therefore receive a larger score. Larger dot-product scores rank first.

## Euclidean distance: compare endpoints

Euclidean distance measures the straight-line gap between vector endpoints.

```text
distance([1, 0], [0.8, 0.2]) = 0.283
```

This is a distance rather than a similarity score, so smaller values rank first.

## Compare the same candidates

Now compare three candidates after defining all three metrics:

| Candidate | Vector | Cosine | Dot product | Euclidean |
|---|---:|---:|---:|---:|
| same direction, longer | `[4.0, 0.0]` | `1.000` | `4.000` | `3.000` |
| nearby endpoint | `[0.8, 0.2]` | `0.970` | `0.800` | `0.283` |
| opposite direction | `[-1.0, 0.0]` | `-1.000` | `-1.000` | `2.000` |

Cosine and dot product rank the longer aligned vector first. Euclidean distance ranks the nearby endpoint first. Every calculation is correct; the metrics measure different relationships.

## Normalization connects the metrics

Normalization rescales a nonzero vector to unit length without changing its direction. For unit vectors:

- cosine similarity equals the dot product;
- Euclidean distance produces the same ordering when smaller distances rank first.

Normalization removes magnitude, so it is not an automatic improvement. Follow the embedding model's guidance and apply the same policy to indexed documents and incoming queries.

## Code walkthrough

The implementation separates calculation from ranking:

- `dot_product` calculates alignment and magnitude.
- `cosine_similarity` divides the dot product by both vector lengths.
- `euclidean_distance` calculates the endpoint gap.
- `l2_normalize` rescales a nonzero vector to unit length.
- `rank` applies the selected metric and the correct score direction.

All comparison functions reject empty vectors and dimension mismatches.

## Choosing and testing a metric

Start with the embedding model's documentation because training determines which comparison is meaningful. Then:

1. Apply the same preprocessing and normalization to documents and queries.
2. Configure the index with the intended metric.
3. Record whether larger or smaller values rank first.
4. Calibrate score thresholds separately for that metric and dataset.
5. Evaluate final rankings with labeled queries from the application.

Tests should cover the relationship each metric claims to measure and the final ranking order, not only individual arithmetic operations.

## Interview questions

### Basic

How does cosine similarity differ from Euclidean distance?

Cosine compares vector direction and largely ignores length. Euclidean distance measures the gap between vector endpoints.

### Intermediate

How does dot product differ from cosine similarity?

Both reward alignment, but dot product includes vector magnitude. They become equal when both vectors have unit length.

### Advanced

How do you choose a vector similarity metric?

Start with the embedding model's guidance, reproduce its preprocessing and normalization, configure the correct score direction, and evaluate the resulting rankings on representative labeled queries.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
