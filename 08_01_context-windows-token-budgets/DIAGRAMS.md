# Diagrams: Context Windows and Token Budgets

## Shared capacity

```text
┌──────────────────────── APPLICATION CONTEXT BUDGET ────────────────────────┐
│ Instructions │ Tools │ Retrieval │ History │ User │ Output │ Safety margin │
└─────────────────────────────────────────────────────────────────────────────┘

Capacity is shared. Output and safety margin must be reserved before flexible
history and retrieval are allocated.
```

## Production flow

```text
User request
     │
     ▼
Classify task and choose budget policy
     │
     ├─────────────── reserve fixed capacity ───────────────┐
     │                                                      │
     ▼                                                      ▼
Rank and select evidence                         Compact conversation state
     │                                                      │
     └───────────────────────┬──────────────────────────────┘
                             ▼
                    Assemble exact request
                             │
                             ▼
                    Count complete payload
                             │
                    ┌────────┴────────┐
                    │ fits            │ overflow
                    ▼                 ▼
                 Execute      Reduce by policy
                    │                 │
                    │          recount or reject
                    └────────┬────────┘
                             ▼
              Record usage, latency, cost, quality
```

## Conversation retention

```text
Original:
[goal] [U1 A1] [U2 A2] [U3 A3] [tool call + result] [U4 A4]

Sliding window:
                                      [tool call + result] [U4 A4]

First plus recent:
[goal]                                [tool call + result] [U4 A4]

Structured memory plus recent:
[goal + decisions + unresolved work]  [tool call + result] [U4 A4]
```

Truncate semantic units. Do not separate a tool result from its call.

## Retrieval selection

```text
Candidates
  ├─ relevant, duplicate ─────┐
  ├─ weak evidence ───────────┼─ remove
  ├─ strong evidence A ───────┐
  ├─ strong evidence B ───────┼─ select, order, then enforce token limit
  └─ complementary evidence C ┘

Final request order:
[stable instructions] [supporting evidence] [strongest evidence] [user query]
```

## Context failure diagnosis

```text
"The agent forgot"
        │
        ├─ Was the fact retrieved?
        │      └─ no → retrieval failure
        │
        ├─ Was it retained after compaction?
        │      └─ no → retention-policy failure
        │
        ├─ Was it in the final counted request?
        │      └─ no → assembly failure
        │
        ├─ Was it buried or contradicted?
        │      └─ yes → ordering/context-quality failure
        │
        └─ Was it present and clear?
               └─ yes → model/prompt behavior; evaluate empirically
```
