# 04.07 - Why Vector Search Alone Misses the Exact Answer

## Learning outcome

Combine dense and lexical rankings without adding incompatible raw scores, preserve one eligibility boundary, and prove whether fusion improves the query slices that matter.

## Complementary errors

A query such as "error E104 after password reset" mixes meaning with an exact identifier. Dense retrieval may understand the password issue but weaken the code. Lexical retrieval can preserve E104 but miss paraphrases. Hybrid search earns its complexity when the two branches make complementary errors.

## Safe fusion

Apply tenant, permission, and metadata eligibility to both branches before fusion. Then combine results using a defined policy:

- **Normalized score fusion** rescales each branch and applies weights. Its behavior depends on the normalization policy.
- **Reciprocal rank fusion (RRF)** uses positions instead of incomparable raw score units.

Candidate depth matters. Fusion cannot rescue a relevant record removed before the branch results meet.

## Evaluation and debugging

Evaluate semantic, exact-identifier, and mixed-query slices. Compare dense-only, lexical-only, and hybrid rankings under the same latency budget. Trace branch candidates, eligibility, component ranks, fusion contributions, and final rank.

## Interview questions

### Basic

Why use hybrid search? Dense and lexical retrieval can recover different relevant documents.

### Intermediate

Why not add cosine and BM25 scores directly? Their scales and distributions do not share a stable unit.

### Advanced

When has hybrid search justified itself? When slice-based evaluation shows enough end-to-end ranking improvement to cover extra search cost, tuning, and operational complexity.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
