# When To Use Multi-Agent Systems

## Core Concepts And Mental Model

More agents do not automatically make a system smarter. They distribute work,
context, tools, and control across multiple model-driven loops. That can help
when the task has real independence or strong boundaries. It can also add
handoffs, duplicated context, latency, cost, and new failure modes.

Use this decision order:

```text
Can stable rules solve it?
  yes -> deterministic workflow
  no  -> does the task need model judgment?
          yes -> start with one agent and tools
                 add multiple agents only when evidence justifies coordination
```

The useful default is simple: choose the smallest architecture that can meet
the requirement.

### Deterministic workflow

Use ordinary software when the inputs, transformations, and decisions are
stable enough to encode directly. Invoice exports, schema validation, retries,
calculations, and fixed approval rules usually belong here.

### Single agent with tools

Use one agent when the task needs model judgment over ambiguous or changing
input, but one control loop can still own the state and choose the right tools.
This is the default agentic architecture because tracing, evaluation, security,
and user interaction stay simpler.

### Multi-agent system

Use multiple agents when separate model-driven loops create a concrete
advantage that one agent cannot provide cleanly. Good evidence includes:

- independent branches that can run in parallel
- large, distinct context windows
- separate tools, permissions, or team ownership
- an independent reviewer checking a producer against evidence
- persistent tool-selection errors after improving tool interfaces

## Important Design Implications

- Coordination is a cost. Every agent boundary needs a task contract, output
  schema, timeout, retry rule, and trace record.
- Parallelism only helps when branches are independent. A chain of dependent
  steps does not get faster because each step has an agent name.
- Context isolation helps only when contexts are truly different. Copying the
  full conversation into every specialist defeats the point.
- Verification is useful when the reviewer has a rubric and evidence. Asking
  the same model to "double check" without criteria is weak control.
- Task value matters. Extra model calls, traces, retries, and operations should
  be justified by the value of better coverage or lower risk.

## Code Map And Implementation Guidance

- `Architecture` names the three outcomes: deterministic workflow, single
  agent with tools, and multi-agent system.
- `WorkloadSignals` captures the evidence and coordination costs.
- `recommend_architecture()` chooses the simplest justified architecture.
- `_multi_agent_benefits()` identifies reasons to split control.
- `_coordination_costs()` identifies reasons to keep the design simpler.
- `demo.py` runs three contrasting scenarios.
- `test_architecture_decision.py` verifies deterministic, single-agent, and
  multi-agent decisions.

The implementation is intentionally deterministic. Replace the scoring policy
only after you can explain which workload signals changed and how tests should
capture the new decision.

## Real Production Considerations And Trade-Offs

Start with a measured single-agent baseline before introducing multiple
agents. Compare task success, latency, token usage, tool calls, failure
recovery, and debugging effort. A multi-agent design that improves one metric
while making operations opaque may not be a better system.

Use durable artifacts for substantial specialist output. A specialist can
write `market_report.json` or `security_findings.json` and return a reference,
rather than forcing the coordinator to rely on a summary of a summary.

Keep authorization outside the prompt. Separate agents may reduce tool
exposure, but service permissions still need to enforce what each component can
do.

## Practical Tips And Common Mistakes

- Do not add agents to make an architecture diagram look advanced.
- Improve tool names, schemas, and dynamic tool loading before splitting one
  agent into many.
- Treat handoffs as interfaces, not casual chat messages.
- Give each specialist a narrow reason to exist.
- Test routing and handoff behavior separately from final answer quality.
- Avoid multi-agent designs when every branch needs the same context.
- Escalate or stop when no component clearly owns the final answer.

## Interview Questions

Basic: What is the first question to ask before choosing a multi-agent design?

Intermediate: What evidence would justify moving from one agent to multiple
agents?

Advanced: How would you prove that a multi-agent design is better than a
single-agent baseline?

## Commands

```bash
cd 09_01_when-to-use-multi-agent-systems
python3 demo.py
python3 -m pytest
```
