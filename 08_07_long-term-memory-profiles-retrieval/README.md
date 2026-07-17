# 8.7 — Long-Term Memory with Profiles and Retrieval

Learner job: design durable memory records that can be retrieved, scoped,
audited, and corrected.

## Architecture Walkthrough

Long-term memory usually has more than one lane:

- profile facts: stable preferences and attributes
- retrieved records: project, account, or domain facts
- episodic memories: past interactions and lessons learned
- audit metadata: source, confidence, timestamps, and ownership

Avoid treating long-term memory as a single text field called `memory`. Durable
memory needs structure.

## Design Decisions

Every memory record should answer:

- who owns this memory?
- what does it claim?
- where did it come from?
- how confident are we?
- when was it created?
- how can it be deleted or corrected?

`long_term_memory.py` models those answers with `MemoryRecord`.

## Implementation Walkthrough

The example store supports:

- `remember` to write a sourced memory
- `profile` to produce stable user facts
- `retrieve` to find task-relevant records
- `provenance` to explain where a memory came from

The retrieval is simple keyword overlap. A larger system might use embeddings,
SQL filters, graph traversal, or a hybrid of all three.

## Production Checklist

- Scope every lookup by user, tenant, or workspace.
- Store provenance with each memory.
- Track confidence separately from the memory value.
- Prefer updating records over appending contradictions forever.
- Make deletion possible before collecting sensitive memory.

## Common Mistakes

Do not use memory without showing where it came from.

Do not mix users in the same retrieval namespace.

Do not treat inferred preferences as confirmed facts.

Do not store sensitive data just because it might be useful later.

## Interview Questions

Basic: What makes long-term memory different from short-term conversation
history?

Intermediate: Why should memory records include source and confidence?

Advanced: How would you design long-term memory so it supports retrieval,
correction, and deletion?

## Commands

```bash
pip install -r requirements.txt
python demo.py
pytest
```
