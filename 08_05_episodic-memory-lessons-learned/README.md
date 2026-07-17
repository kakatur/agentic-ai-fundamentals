# 8.5 — Episodic Memory and Lessons Learned

Learner job: store past interactions as concrete episodes and retrieve the
ones that can improve the next decision.

## Pattern

Episodic memory stores selected past interactions as records the agent can use
later. A useful episode captures:

- task
- action
- outcome
- lesson
- tags for retrieval

The lesson is the reusable part. The full episode explains where that lesson
came from.

## When To Use This

Use episodic memory when the agent improves by remembering what happened before:

- previous troubleshooting attempts
- customer support resolutions
- failed tool calls and fixes
- successful plans for similar tasks
- user-specific preferences with clear consent

Avoid storing every token the user typed. Keep episodes selected, explainable,
and relevant to future decisions.

## Implementation Walkthrough

`episodic_memory.py` keeps each episode small and inspectable. Retrieval uses
shared tags instead of embeddings so the behavior is obvious in tests.

A larger version can replace tag matching with vector search, but the record
shape should stay explicit. You need to know whether the agent is using a past
outcome, a reusable lesson, or a vague memory.

## Anti-Patterns

Do not store raw private conversation when a distilled lesson would be enough.

Do not retrieve episodes without checking relevance to the current task.

Do not promote a lesson from a single failure into a universal rule without
review.

Do not hide memory use from debugging logs.

## Extension Ideas

Add confidence to each episode.

Add human review before promoting lessons.

Add expiration so stale operating rules stop influencing future decisions.

## Interview Questions

Basic: What is an episode in agent memory?

Intermediate: Why should an episode include outcome along with task and action?

Advanced: How would you prevent a bad past episode from poisoning future agent
decisions?

## Commands

```bash
pip install -r requirements.txt
python demo.py
pytest
```
