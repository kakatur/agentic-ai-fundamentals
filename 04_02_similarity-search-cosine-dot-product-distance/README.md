# 04.02 - Why Vector Similarity Metrics Disagree

## Learning outcome

Calculate three common vector metrics, predict how each one ranks candidates, and keep metric direction and normalization consistent from indexing through querying.

## One query, three reasonable winners

Lesson 4.1 produced comparable query and document vectors. That still does not tell a search system which document belongs first. The same vectors can produce different rankings because each metric answers a different geometric question.

Use one query and three candidates throughout this lesson. Before calculating anything, try to predict which candidate should win:

```text
query                 [1.0, 0.0]
same direction        [4.0, 0.0]
nearby endpoint       [0.8, 0.2]
opposite direction   [-1.0, 0.0]
```

## Cosine similarity compares direction

Cosine similarity divides the dot product by both vector lengths. It measures the angle between vectors, so `[1, 0]` and `[4, 0]` receive `1.0` even though their lengths differ.

- `1` means the same direction.
- `0` means perpendicular directions.
- `-1` means opposite directions.
- Larger values rank first.

Cosine is useful when direction carries the intended signal and magnitude should not change the ranking.

## Dot product keeps magnitude

The dot product multiplies corresponding coordinates and adds them:

```text
(1 x 4) + (0 x 0) = 4
```

Alignment and candidate magnitude both affect the result. Larger values rank first. This can be the correct contract when model training makes vector magnitude meaningful.

## Euclidean distance compares endpoints

Euclidean distance measures the straight-line gap between endpoints:

```text
sqrt((1 - 0.8)^2 + (0 - 0.2)^2) = 0.283
```

It is a distance, so smaller values rank first. Some libraries return squared Euclidean distance because removing the square root preserves order; check the API before interpreting a returned value as a physical distance.

## Why the rankings differ

| Candidate | Cosine | Dot product | Euclidean |
|---|---:|---:|---:|
| same direction | `1.000` | `4.000` | `3.000` |
| nearby endpoint | `0.970` | `0.800` | `0.283` |
| opposite direction | `-1.000` | `-1.000` | `2.000` |

Cosine and dot product prefer the aligned long vector. Euclidean prefers the nearby endpoint. The difference comes from the geometric relationship each metric measures.

## Normalization connects the metrics

L2 normalization rescales each nonzero vector to length one. For unit vectors:

- cosine similarity equals the dot product;
- squared Euclidean distance equals `2 - 2 * dot_product`;
- all three produce the same ordering when their sort directions are correct.

Normalization removes magnitude. Apply it only when the embedding model and index contract call for it, and apply it to both stored and query vectors.

## Code and tests

[`metrics.py`](metrics.py) separates metric calculation from ranking. The `rank` function stores whether larger or smaller scores are better, preventing a common bug where Euclidean results are sorted backward.

The tests cover arithmetic, vector validation, normalized ordering, metric selection, and sort direction. Add a ranking-level test whenever you change the index configuration; correct formulas can still feed an incorrect ordering policy.

## Decision checklist

1. Start with the embedding model's documented metric and preprocessing.
2. Configure the index with the same metric.
3. Record whether the API returns similarity, distance, or squared distance.
4. Calibrate thresholds separately for each model, metric, and dataset.
5. Evaluate ranked results with labeled queries; a plausible score has no universal meaning.

## Interview questions

### Basic

**How does cosine similarity differ from Euclidean distance?**

Cosine compares direction after dividing out length. Euclidean measures the distance between endpoints.

### Intermediate

**When are cosine similarity and dot product equal?**

When both vectors are L2-normalized to unit length.

### Advanced

**How do you choose a metric for an embedding index?**

Follow the model's metric and preprocessing contract, reproduce it for ingestion and queries, confirm score direction in the database API, and evaluate rankings on representative labeled data.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
