# 04.07 - Hybrid Search: When Meaning Misses the Exact Match

## Learning outcome

Combine dense and lexical rankings with a defined fusion policy, enforce one eligibility boundary, and evaluate semantic, identifier, and mixed queries separately.

## Meaning finds the problem. Exact search finds the code.

Consider the query `error E104 after password reset`. The phrase contains two kinds of evidence: a concept about password recovery and an exact identifier that must survive unchanged.

- Dense retrieval can find paraphrases around password recovery while overlooking the rare code.
- Lexical retrieval can preserve `E104`, names, and quoted phrases while missing related wording.

Each branch can return a plausible but incomplete ranking. Fusion becomes useful when their errors are complementary. It still cannot recover a document missing from both candidate lists, which gives us the central question for this lesson: how do we combine the evidence without pretending the two score scales mean the same thing?

## Keep eligibility consistent

Tenant, permission, date, and metadata rules must apply to both branches. Filter before fusion so ineligible documents cannot consume candidate slots, affect ranks, or appear in traces.

## Choose a fusion policy

Raw cosine-like and BM25 scores do not share a stable unit. Adding them directly gives the larger numeric scale accidental control.

Two useful policies are:

- **Normalized score fusion:** normalize each branch with an explicit policy, apply weights, then add. Outliers and query-dependent score distributions can affect the result.
- **Reciprocal rank fusion (RRF):** combine positions using `weight / (k + rank)`. RRF avoids raw-score calibration and discards score-gap information.

[`hybrid.py`](hybrid.py) implements weighted RRF with deterministic tie-breaking. Start with simple weights, then tune only from labeled evaluation data.

## Candidate depth sets a ceiling

If the correct runbook ranks eleventh in a branch that returns ten candidates, fusion never sees it. Increasing branch depth can improve recall and also increase latency and fusion work.

Diagnose these cases separately:

1. Missing from both branches: improve retrieval or increase candidate depth.
2. Present but filtered: inspect eligibility data and policy.
3. Present after filtering but ranked poorly: inspect fusion contributions.

## Trace and evaluate

Log branch candidates, component ranks, eligibility decisions, contribution per branch, final score, and final rank. Avoid logging sensitive document text when IDs and policy-safe metadata are enough.

Evaluate three query slices: semantic, exact identifier, and mixed. Compare dense-only, lexical-only, and hybrid results under the same latency budget. Report slice metrics as well as the aggregate so gains in one group cannot hide regressions in another.

## Research note

RRF was introduced as a simple rank-combination method in [Cormack, Clarke, and Buettcher, SIGIR 2009](https://cormack.uwaterloo.ca/cormack/cormacksigir09-rrf.pdf). Product-specific hybrid implementations may use different normalization and fusion defaults; inspect the active version.

## Interview questions

### Basic

**Why use hybrid search?** Dense and lexical retrievers can recover different relevant documents from the same query.

### Intermediate

**Why avoid adding raw dense and BM25 scores?** Their scales and distributions do not represent the same unit.

### Advanced

**When has hybrid search earned its complexity?** When slice-level evaluation shows useful end-to-end gains that justify added latency, tuning, tracing, and failure modes.

## Commands

```bash
python3 demo.py
python3 -m unittest -v
```
