# Debugging Multi-Agent Systems

## Core Concepts And Mental Model

Debugging multi-agent systems is mostly boundary debugging. The failure may
look like a bad final answer, but the cause is often earlier:

- the wrong agent was selected
- a handoff lost context
- a branch reused stale state
- two agents bounced the task back and forth
- nobody owned the final answer

Do not start by reading every prompt. Start with a trace.

## Important Design Implications

- Every handoff needs sender, receiver, reason, state version, and payload
  summary.
- Trace events should be structured enough for tests and detectors.
- Loops need explicit limits.
- State versions make stale reads visible.
- Debugging should separate routing, state, tool, and model failures.

## Code Map And Implementation Guidance

- `TraceEvent` records one step in the workflow.
- `detect_repeated_handoffs()` catches handoff loops.
- `detect_stale_state()` catches state regressions.
- `detect_unanswered_task()` catches traces with no final owner.
- `analyze_trace()` combines the detectors.

This lesson debugs deterministic traces. The same shape works with model-backed
agents if the runtime records structured events.

## Real Production Considerations And Trade-Offs

Full traces can become noisy and sensitive. Store enough to debug boundaries:
agent names, action types, state versions, route decisions, tool names, and
sanitized payload summaries. Avoid logging raw secrets, unnecessary personal
data, or private chain-of-thought.

The goal is not maximum logging. The goal is reconstructing why the workflow
made a decision.

## Practical Tips And Common Mistakes

- Add run IDs and task IDs to every event.
- Record state version at handoff time.
- Set handoff and retry limits.
- Keep a small library of trace detectors.
- Reproduce failures with deterministic fixtures.

## Interview Questions

Basic: What should be present in a useful multi-agent trace?

Intermediate: How would you detect an infinite handoff loop?

Advanced: How would you debug a bad answer without exposing private reasoning?

## Commands

```bash
cd 09_08_debugging-multi-agent-systems
python3 demo.py
python3 -m pytest
```
