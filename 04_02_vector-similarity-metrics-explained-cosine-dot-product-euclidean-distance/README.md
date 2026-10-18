# 4.2 - Vector Similarity Metrics Explained: Cosine, Dot Product, and Euclidean Distance

## Learning outcome

By the end of this lesson, you can calculate cosine similarity, dot product, and Euclidean distance; explain why they rank the same candidates differently; and keep metric direction and preprocessing consistent from indexing through querying.

## The problem: comparable vectors still need a ranking rule

Lesson 4.1 turned text into vectors. A vector gives a piece of text a location or direction in a numeric space, but the vector alone does not tell a search system which candidate belongs first.

The ranking depends on the metric. Each metric asks a different geometric question, so the same query and candidates can produce different winners.

We will use one small example throughout the lesson:

```text
query                 [1.0, 0.0]
same direction        [4.0, 0.0]
diagonal              [5.0, 2.0]
nearby endpoint       [0.8, 0.6]
```

Before calculating anything, make a prediction. One candidate points in exactly the same direction as the query, but is much longer. Another points diagonally with a larger magnitude. The third endpoint is physically nearby. Which relationship should your search treat as most relevant?

## The metric contract

Treat a metric as part of the index contract, not as a cosmetic setting. Your code needs to know both what a score means and which direction is better.

| Metric | Measures | Returned value in this lesson | Better result |
|---|---|---|---|
| Cosine similarity | Direction or angle | Similarity | Larger |
| Dot product | Alignment and magnitude | Similarity | Larger |
| Euclidean distance | Endpoint gap | Distance | Smaller |

This lesson's Python code returns positive Euclidean distance. Libraries may expose a different convention: squared L2 distance, negative Euclidean similarity, cosine distance, or a negative inner product. Always read the API contract before choosing `ORDER BY`, sorting a result list, or setting a threshold.

## Cosine similarity compares direction

Cosine similarity divides the dot product by both vector lengths. Geometrically, it measures the angle between two nonzero vectors:

```text
cos(x, y) = (x · y) / (||x|| ||y||)
```

A zero vector has no direction, so cosine similarity is undefined for it. The
Python implementation raises `ValueError` when either input is zero, and
`l2_normalize` also rejects a zero vector rather than returning another zero
vector.

For the query `[1, 0]` and the candidate `[4, 0]`, calculate the score step by step:

```text
cos([1, 0], [4, 0])
= (1 x 4 + 0 x 0) / (1 x 4)
= 4 / 4
= 1.0
```

The vectors have different lengths, but they point in exactly the same direction. The factor of four cancels because their angle is zero.

For nonzero vectors:

- `1` means the same direction;
- `0` means perpendicular directions;
- `-1` means opposite directions;
- larger values rank first.

Cosine is useful when the direction of an embedding carries the intended signal and vector length should not change the ranking. For text embeddings, direction often captures semantic relationships more reliably than raw vector length, which is why cosine similarity is common. Still, follow the embedding model's metric contract. Its scores are bounded between `-1` and `1` for nonzero vectors.

## Dot product keeps magnitude

The dot product multiplies matching coordinates and adds the products:

```text
(1 x 4) + (0 x 0) = 4
```

The result reflects both alignment and length. The diagonal candidate scores `5.0`, the long same-direction candidate scores `4.0`, and the nearby candidate scores `0.8`. Unlike cosine similarity, a dot product is not limited to the range `-1` to `1`; a larger vector can produce a larger score when its direction is useful.

That behavior can be exactly what a model's training objective expects. It can also be wrong for a model whose magnitude should be ignored. The decision comes from the embedding model's metric and preprocessing contract, followed by evaluation on your own labeled queries.

## Euclidean distance compares endpoints

Euclidean distance treats vectors as points and measures the straight-line gap between their endpoints. The general equation is:

```text
d(x, y) = sqrt(sum_i((x_i - y_i)^2))
```

For the query `[1, 0]` and the nearby candidate `[0.8, 0.6]`, substitute the coordinates step by step:

```text
d([1, 0], [0.8, 0.6])
= sqrt((1 - 0.8)^2 + (0 - 0.6)^2)
= sqrt(0.2^2 + (-0.6)^2)
= sqrt(0.4)
≈ 0.632
```

Euclidean distance is sensitive to both direction and magnitude because it compares endpoint positions.

The long aligned candidate is three units from the query:

```text
sqrt((1 - 4)^2 + (0 - 0)^2) = 3.000
```

Because this is a distance, smaller values rank first. Squared Euclidean distance is often used in implementations because it avoids the square root. Squaring preserves order for nonnegative distances, but `9.0` is a squared distance, not a three-unit physical distance. Keep the distinction clear when logging scores or explaining thresholds.

## Why the rankings disagree

Here are the scores for the same vectors:

| Candidate | Cosine | Dot product | Euclidean |
|---|---:|---:|---:|
| same direction | `1.000` | `4.000` | `3.000` |
| diagonal | `0.928` | `5.000` | `4.472` |
| nearby endpoint | `0.800` | `0.800` | `0.632` |

Cosine ranks the same-direction vector first, dot product ranks the diagonal vector first, and Euclidean distance ranks the nearby endpoint first. All three calculations are correct because they measure different relationships.

That distinction matters in a real index. A bug does not need to be in the formula itself. You can calculate a Euclidean distance correctly and still return the wrong document by sorting from largest to smallest. The metric name, score convention, and sort direction must travel together.

## Normalization connects the metrics

L2 normalization rescales each nonzero vector so its length becomes one while preserving its direction. For unit vectors, the dot product equals cosine similarity:

```text
cosine(q, x) = dot(q, x)
```

### Why normalize for cosine search?

Cosine similarity normally requires the dot product divided by both vector lengths:

```text
cosine(A, B) = dot(A, B) / (length(A) * length(B))
```

After normalization, every vector has length `1`, so the denominator is `1 * 1` and cosine similarity becomes the dot product. Without normalization, every comparison must calculate both lengths and perform a division. Normalizing article vectors once during vector creation lets a vectorized search use one dot-product operation, such as a NumPy matrix multiplication, instead of repeating that work for every candidate.

This provides faster searches, consistent preprocessing between saved article vectors and new query vectors, rankings based on direction rather than magnitude, and less repeated work when the same articles are searched many times. Normalization is therefore an implementation optimization for cosine similarity, not an alternative to it. Both the article vectors and the search-query vector must be normalized for their dot product to equal cosine similarity.

The squared Euclidean distance has a matching identity:

```text
||q - x||² = 2 - 2 * dot(q, x)
```

So cosine similarity, dot product, and Euclidean distance produce the same ordering for unit vectors when you sort each result in the correct direction. The numerical values still have different meanings: cosine and dot product are similarities, while Euclidean is a distance.

Normalization removes magnitude, so it is a deliberate modeling choice. Apply it only when the embedding model and index contract call for it.

## Implementation and tests

[`metrics.py`](metrics.py) keeps the formulas separate from the ranking policy. `dot_product`, `cosine_similarity`, and `euclidean_distance` each calculate one relationship. The `rank` function pairs each metric with a `larger_is_better` flag, so Euclidean results sort ascending while the two similarity scores sort descending.

Run the demo to see the ordering directly:

```text
cosine
  +1.000  same direction, longer
  +0.928  diagonal
  +0.800  nearby endpoint

dot
  +5.000  diagonal
  +4.000  same direction, longer
  +0.800  nearby endpoint

euclidean
  +0.632  nearby endpoint
  +3.000  same direction, longer
  +4.472  diagonal
```

The tests cover arithmetic, dimension validation, normalized metric equivalence, metric selection, and final sort direction. The ranking-level test is important: correct formulas can still feed an incorrect ordering policy.

The vectors here are a controlled two-dimensional example. They prove the arithmetic and the contract, not the quality of a production embedding model. Use representative labeled queries to measure whether your chosen metric returns useful documents near the top.

## Decision checklist

1. Read the embedding model's documented metric and preprocessing requirements.
2. Use the same metric and preprocessing for document ingestion and query encoding.
3. Record whether your library returns similarity, distance, squared distance, or a negated score.
4. Verify the sort direction in the index and in application-side ranking code.
5. Calibrate thresholds separately for each model, metric, and dataset.
6. Evaluate ranked results with labeled queries; a plausible score has no universal meaning.

## Interview questions

### Basic

**How does cosine similarity differ from Euclidean distance?**

Cosine compares direction after accounting for vector length. Euclidean measures the straight-line distance between endpoints.

### Intermediate

**When are cosine similarity and dot product equal?**

When both vectors are L2-normalized to unit length. The dot product then contains the same directional information as cosine similarity.

### Advanced

**How do you choose a metric for an embedding index?**

Follow the model's metric and preprocessing contract, reproduce it for ingestion and queries, confirm the score convention and sort direction in the database API, and evaluate rankings on representative labeled data.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```

## References

- Sentence Transformers similarity functions and normalized embeddings: https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html
- Faiss metric and distance conventions: https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances
- pgvector operators and score conversions: https://github.com/pgvector/pgvector
