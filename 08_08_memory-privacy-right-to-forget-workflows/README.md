# 8.8 — Memory Privacy and Right-to-Forget Workflows

Learner job: design memory so users can inspect, export, suppress, and delete
stored information.

## Production Readiness Problem

Agent memory creates privacy risk when it is easy to write and hard to remove.
Plan these fields before the first memory is stored:

- record owner
- record category
- consent state
- source
- export path
- deletion path
- audit event

This lesson is engineering guidance, not legal advice. For GDPR-specific work,
review the actual regulation and involve qualified counsel.

## Right-To-Forget Workflow

A practical deletion workflow should:

1. find all records owned by the user
2. delete or anonymize those records according to policy
3. suppress future writes until the user opts back in
4. write an audit event
5. propagate deletion to downstream stores and caches

[GDPR Article 17](https://gdpr-info.eu/art-17-gdpr/) describes a right to
erasure in several circumstances and also lists exceptions. That means the
engineering workflow needs policy input; the code cannot decide legal
eligibility by itself.

## Implementation Walkthrough

`memory_privacy.py` demonstrates a privacy-aware store:

- `PrivateMemory` includes user, category, value, and consent
- `remember` rejects records without consent
- `export_user` returns only one user's memories
- `delete_user` removes records and suppresses future writes
- `audit_log` records memory actions

The example is in-memory. The same contract applies to databases, vector
stores, caches, and analytics copies.

## Common Mistakes

Do not store memory before you know how to delete it.

Do not delete the primary database while leaving vector indexes and caches
untouched.

Do not rely on free-form text search to find a user's records.

Do not treat audit logs as a place to store the deleted private value.

## Privacy Checklist

- User-scoped keys exist for every memory.
- Consent or policy basis is recorded before write.
- Export returns a complete user-scoped view.
- Delete covers primary records, indexes, caches, and derived memories.
- Future writes are blocked after deletion until allowed again.
- Audit records actions without re-storing sensitive content.

## Interview Questions

Basic: Why is memory deletion harder than deleting one database row?

Intermediate: Why should a memory store suppress future writes after a deletion
request?

Advanced: How would you design deletion propagation across a SQL database,
vector index, semantic cache, and analytics pipeline?

## Commands

```bash
pip install -r requirements.txt
python demo.py
pytest
```
