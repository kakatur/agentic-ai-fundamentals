# State Management in Multi-Agent Systems

## Core Concepts And Mental Model

State is the workflow's memory. It is not the same thing as an agent's private
scratchpad and it is not the same thing as the final answer. Good shared state
holds the facts that other steps are allowed to depend on.

In a multi-agent system, state answers four questions:

- What task are we working on?
- What has already been decided?
- What evidence has crossed an agent boundary?
- Where can we resume after failure?

The safest default is typed, append-friendly state with explicit reducers and
checkpoints.

## Important Design Implications

- Shared state should be small and intentional.
- Agent scratchpads should not leak into global state by default.
- Parallel agents need reducer rules for conflicts and append-only fields.
- Checkpoints should happen at workflow boundaries, not only at the end.
- Tests should assert state transitions, not just the final prose response.

## Code Map And Implementation Guidance

- `WorkflowState` is the typed state object.
- `StatePatch` is what agents return.
- `merge_state()` is the reducer. It replaces scalar decisions but appends
  messages, facts, and risks.
- `Checkpointer` stores snapshots by task ID.
- `run_workflow()` routes, assesses risk, decides, and saves each boundary.

The implementation is intentionally deterministic. In a model-backed workflow,
keep the same state contract and test the reducer separately from model output.

## Real Production Considerations And Trade-Offs

State is powerful because it lets agents coordinate. It is dangerous because
bad state spreads. Avoid dumping every message, raw prompt, and intermediate
thought into shared state. Store durable facts, decisions, references, and
review reasons.

For concurrent branches, define conflict behavior before you run them. Lists
usually append. Sets deduplicate. A single `decision` field needs ownership or
priority rules.

## Practical Tips And Common Mistakes

- Version state snapshots.
- Make reducers deterministic.
- Keep personally sensitive data out of broad shared state.
- Save checkpoints before and after risky steps.
- Test resume from a checkpoint, not only a clean run.

## Interview Questions

Basic: What belongs in shared state versus an agent scratchpad?

Intermediate: How should parallel branches merge updates into one state?

Advanced: How would you design checkpointing for a workflow with human review?

## Commands

```bash
cd 09_05_state-management-in-multi-agent-systems
python3 demo.py
python3 -m pytest
```
