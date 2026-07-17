# 8.3 — Short-Term Memory and Conversation Windows

Learner job: keep enough recent conversation for continuity without stuffing
the whole chat history into every call.

## What Problem This Solves

Short-term memory answers questions like:

- What did the user just ask?
- What did the assistant just promise?
- Which facts must survive even when old turns are trimmed?

Short-term memory is the current working conversation window. Long-term memory
belongs in a different store with different retention and privacy rules.

## Window Strategy

Use two lanes:

- pinned facts for durable session facts such as name, preference, active task,
  or selected account
- recent message pairs for conversational flow

Trimming only by message count can break context. If you keep an assistant
answer but drop the user question that caused it, the model sees an orphaned
answer. Trim in turns or pairs instead.

## Implementation Walkthrough

`session_memory.py` uses immutable `Message` records and three operations:

- `add_message` validates roles
- `trim_to_recent_pairs` keeps the newest user-led turns
- `build_conversation_window` combines pinned facts with recent messages

This keeps the memory policy small enough to test. You can replace the in-memory
tuple with a database-backed history later.

## Common Mistakes

Do not treat every old message as equally valuable.

Do not bury pinned facts inside trimmed history.

Do not summarize away commitments the assistant already made.

Do not assume the model remembers anything that is not in the current call.

## Hands-On Exercise

Extend `build_conversation_window` so each pinned fact has a source message ID.
Then add a test that proves a fact can be traced back to the turn that created
it.

## Interview Questions

Basic: What is short-term memory in an agent conversation?

Intermediate: Why is trimming by conversation pairs safer than trimming by raw
message count?

Advanced: How would you combine pinned session facts, recent history, and a
token budget in one memory policy?

## Commands

```bash
pip install -r requirements.txt
python demo.py
pytest
```
