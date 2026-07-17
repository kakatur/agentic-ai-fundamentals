# 8.4 — Semantic Caching for Faster Agents

Learner job: decide when an old answer is similar enough to reuse and when the
agent must call the model again.

## When To Use This

Semantic caching works best for repeated support answers, documentation lookup,
policy explanations, and other requests where many users ask similar questions.

It is risky for personalized, high-stakes, rapidly changing, or permissioned
answers unless the cache key includes the safety boundary.

## Decision Rule

A cache hit needs three things:

- semantic similarity above a threshold
- compatible safety label or task type
- response that is still valid for the current policy and user

The threshold is a product decision. A lower threshold saves more calls but
increases the chance of reusing the wrong answer.

## Implementation

`semantic_cache.py` uses a tiny bag-of-words cosine similarity scorer so the
lesson has no external dependencies. A production cache would usually replace
this with embeddings and a vector index.

The same cache policy applies no matter which embedding provider you use:

- store prompt, response, and safety label
- score the new prompt against cached prompts
- return only the best hit above threshold
- partition sensitive workflows with labels

## Trade-Offs

Speed improves because the model call is skipped.

Cost improves because repeated questions are answered from storage.

Quality can drop if the threshold is too loose or if old answers remain valid
after policy changes.

Privacy risk increases if personalized answers are cached without user or
tenant boundaries.

## Test Walkthrough

The tests cover normalization, related-text scoring, thresholded hits, and
safety-label isolation. The safety-label test catches a common failure: similar
text is not enough when the workflows have different risk.

## Interview Questions

Basic: What is the difference between exact caching and semantic caching?

Intermediate: Why should semantic caches use thresholds and safety labels?

Advanced: How would you invalidate cached answers after a policy change or
model behavior change?

## Commands

```bash
pip install -r requirements.txt
python demo.py
pytest
```
