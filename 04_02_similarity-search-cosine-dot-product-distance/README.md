# 04.02 - The Similarity Metric Mistake That Scrambles Search Results

## Learning outcome

Implement cosine similarity, dot product, and Euclidean distance; predict how normalization changes rankings; and choose a metric from an embedding model's contract and retrieval evidence.

## One dataset, different winners

A metric defines what "near" means. Dot product rewards alignment and magnitude. Cosine compares direction by dividing out magnitude. Euclidean distance measures straight-line separation and sorts smaller values first.

For unit vectors, cosine and dot product produce the same ranking. That does not mean normalization is always correct: vector magnitude may carry model-specific information.

## Debugging checklist

- Record the metric with every index version.
- Keep document and query preprocessing identical.
- Make score direction explicit: similarities descend; distances ascend.
- Reject dimension mismatches and define zero-vector behavior.
- Compare approximate search with an exact baseline before blaming embeddings.
- Evaluate rankings on labeled queries rather than interpreting raw scores alone.

## Interview questions

### Basic

How does cosine similarity differ from Euclidean distance? Cosine compares direction; Euclidean distance compares spatial separation.

### Intermediate

When do cosine and dot product agree? When vectors are normalized to unit length, cosine's denominator becomes one.

### Advanced

How do you choose a metric? Start with the model provider's training guidance, reproduce its preprocessing, and validate ranking quality and thresholds on representative labeled data.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
