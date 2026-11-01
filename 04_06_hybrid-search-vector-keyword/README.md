# 4.6 — Hybrid Search: When Meaning Misses the Exact Match

## Learning outcome

Combine dense and lexical retrieval rankings with reciprocal rank fusion, apply the same eligibility rules to both branches, and test whether the combination improves the query types your users submit.

## One query, two kinds of evidence

A support engineer searches for `error E104 after password reset`.

The phrase has a meaning: the user is troubleshooting account recovery. It also has an exact identifier: `E104` must remain intact. Dense retrieval can find a paraphrased password-reset explanation. Lexical retrieval can reward the rare error code. Either branch can miss the useful document on its own.

Hybrid retrieval runs both branches, then combines their candidate rankings. It helps when the branches make complementary errors and the relevant result appears in at least one candidate list.

## Keep one eligibility boundary

Both branches must use the same tenant, permission, date, and metadata rules. If dense and lexical search see different eligible records, their ranks describe different result sets and fusion can surface an item the caller should not see.

Apply eligibility before the branch results are fused. Deduplicate IDs before calculating the final list. Keep the source record and ID mapping so the returned result resolves to the current content.

## Why rank positions are useful

A cosine score and a lexical score such as BM25 do not use the same scale. Adding their raw values gives whichever score happens to have larger numbers more influence.

Reciprocal rank fusion, or RRF, combines positions instead:

```text
RRF(document) = sum over retrievers of weight / (constant + rank)
```

A document's first-place rank contributes more than its tenth-place rank. The constant smooths the difference between rank positions. RRF ignores score gaps inside a branch, so it is simple to combine and easy to trace; it also discards information about how strongly a branch preferred one candidate over another.

## Work the E104 example

Assume both retrievers use the same eligible records and return their top candidates. With equal weights and an illustrative constant of 10:

| Document | Dense rank | Lexical rank | RRF calculation | RRF score |
|---|---:|---:|---|---:|
| Password-reset FAQ | 2 | 5 | 1/12 + 1/15 | 0.1500 |
| E104 troubleshooting runbook | 6 | 1 | 1/16 + 1/11 | 0.1534 |
| General account-access article | 1 | 8 | 1/11 + 1/18 | 0.1465 |

The exact-code runbook moves to the top because lexical search ranked it first, while dense search still contributes evidence for the other candidates. The numbers are a worked example, not a default configuration. Choose the smoothing constant, branch weights, and candidate depths using a labeled query set.

A useful trace records each candidate's ID, eligibility decision, rank in each branch, contribution to the fused score, and final position. If a result is missing, ask whether it was absent from both branch lists, removed by an eligibility rule, or present but ranked too low after fusion.

## Implement the rank combination

The lesson repository includes `hybrid.py`, whose `reciprocal_rank_fusion` function accepts ordered document-ID lists, a `rank_constant`, and optional branch `weights`. It assigns one-based ranks, counts a document at most once per branch, sums weighted reciprocal-rank contributions, and sorts by score with a stable ID tie-break.

The accompanying `demo.py` uses the E104 worked rankings and prints the three named documents' scores:

```bash
python3 demo.py
python3 -m unittest -v
```

This combines already-filtered candidate lists. Apply authorization and metadata eligibility consistently before calling the fusion function; rank fusion cannot repair an access-control mismatch or recover a document absent from every candidate list.

## Candidate depth limits the result

Fusion cannot recover a document that neither branch returned. If the relevant runbook ranks below a branch's candidate limit, increase the candidate depth or improve that branch before tuning RRF. Deeper lists can increase search and fusion work, so compare quality and latency together.

Evaluate at least three query slices:

- **Semantic:** paraphrases with few shared terms.
- **Identifier-heavy:** error codes, product names, SKUs, or exact phrases.
- **Mixed:** queries that combine a concept with an exact token.

Compare dense-only, lexical-only, and hybrid retrieval on the same records, filters, and labels. Reuse the workload card and labeled query set from Lesson 4.4, then add the chunking policy from Lesson 4.5. Hybrid search earns its complexity when it improves the slices that matter and meets the application's latency and operating limits; replay this final retrieval design in the backend evaluation before making a durable choice.

## Common failure modes

- Adding raw dense and lexical scores without a calibrated normalization policy.
- Applying permissions in one retrieval branch but forgetting the other.
- Letting duplicate records occupy several fused positions.
- Fusing shallow candidate lists that never contained the answer.
- Reporting one aggregate metric that hides a regression on identifier queries.

## Interview questions

### Basic

**When is hybrid search useful?**

When dense and lexical retrieval find different relevant records, such as paraphrased meaning in one branch and exact identifiers in the other.

### Intermediate

**Why does reciprocal rank fusion avoid raw score addition?**

It combines rank positions, so the two branches do not need their raw scores to share a numeric scale. It gives up information about the score gaps within each branch.

### Advanced

**How would you decide whether hybrid search is worth operating?**

Apply identical eligibility rules, compare dense-only, lexical-only, and fused results on semantic, identifier, and mixed query slices, then check relevance, candidate depth, latency, traceability, and maintenance cost.

## References

- Cormack, Clarke, and Büttcher, “Reciprocal Rank Fusion,” SIGIR 2009 — https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
- PostgreSQL full-text search introduction — https://www.postgresql.org/docs/current/textsearch-intro.html
- pgvector hybrid search with PostgreSQL full-text search — https://github.com/pgvector/pgvector

Documentation checked: 2026-10-04. Recheck version-sensitive implementation details before recording.
