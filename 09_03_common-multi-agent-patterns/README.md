# Common Multi-Agent Patterns

Multi-agent systems are easier to reason about when you name the coordination
pattern before choosing a framework. The pattern determines who owns routing,
what context crosses each boundary, how partial work is merged, and what
happens when an agent is uncertain.

This lesson uses deterministic Python instead of LLM calls. That keeps the
coordination mechanics visible: every "agent" has a narrow scope, every handoff
has a record, and every test can assert the workflow contract directly.

## Core concepts and mental model

### Pattern first, framework second

A multi-agent design is not just "several prompts." It is a control-flow
choice. Start by deciding which shape the work has:

```text
coordinator-router      request -> coordinator -> one specialist -> answer
parallel specialists    request -> coordinator -> many specialists -> merge
producer-verifier       request -> producer -> verifier -> accept or escalate
human escalation         uncertain agent -> human review queue
```

These shapes can be implemented with ordinary functions, tool wrappers,
LangGraph, services, queues, or an agent framework. The important part is the
runtime contract.

### Coordinator-router

A coordinator-router keeps one component responsible for selecting the next
agent. Specialists do not compete directly for the user turn. The coordinator
passes a narrow task payload and records why that specialist was selected.

Use this when requests naturally belong to one domain:

- billing
- account security
- technical support
- policy review

The main risk is routing quality. If descriptions overlap or the coordinator
receives too little context, the wrong specialist can produce a confident but
irrelevant answer.

### Parallel specialists

Parallel specialists work independently on different parts of the same request.
The coordinator merges their replies into one result.

Use this when the branches are meaningfully independent:

```text
                         ┌─> billing_agent ──┐
request -> coordinator ──┼─> security_agent ─┼─> merge
                         └─> technical_agent ┘
```

The merge step is a first-class design problem. It must decide how to combine
facts, confidence, citations, failures, and conflicting recommendations. Do not
hide that logic inside free-form prose.

### Producer-verifier

A producer-verifier pattern separates generation from checking. The verifier
receives the original task and the producer's answer. It can accept, reject, or
send the result to another step.

This pattern is useful when an independent check can catch expensive failures:

- compliance review
- code generation against tests
- financial calculations
- evidence-backed research

The verifier is only valuable when it has a clear rubric and access to the
evidence it needs. Asking another model to "double check" without criteria is
not a strong control.

### Human escalation

Escalation is a coordination pattern, not a last-minute error message. The
system should define when uncertainty, missing context, policy limits, or high
priority force human review.

Good escalation preserves:

- the original task
- the selected route
- the agent's confidence
- the reason for escalation
- enough context for the human to continue without restarting

## Important design implications

### Handoffs are interfaces

Every agent boundary should specify:

- sender and receiver
- reason for the handoff
- payload shape
- expected output
- timeout or failure behavior
- trace fields

The `Handoff` dataclass in this lesson makes that boundary explicit. In a real
system, the same contract might be a Pydantic model, JSON schema, queue message,
or tool call.

### Confidence is not correctness

The example agents return a numeric confidence so tests can show escalation
behavior. In production, confidence should be calibrated against measured
outcomes. Treat model self-confidence as a weak signal unless you have validated
it for the task.

### Merge logic carries product policy

Parallel work is only useful if the join step knows what to do with partial
results. A support workflow might prefer the safest answer. A research workflow
might preserve competing hypotheses. An incident workflow might escalate if any
specialist reports a severe risk.

### Specialists need narrow context

Passing the full conversation to every specialist is simple but often defeats
the purpose of specialization. Prefer task-specific payloads that include the
objective, relevant context, constraints, and required output format.

## Code map and implementation guidance

- `patterns.py`
  - `Task`, `AgentReply`, `Handoff`, and `WorkflowResult` define the workflow
    contracts.
  - `SpecialistAgent` simulates a scoped specialist with deterministic routing
    evidence.
  - `Coordinator.run_router_pattern()` demonstrates one-specialist routing and
    escalation.
  - `Coordinator.run_parallel_pattern()` demonstrates fan-out and merge.
  - `VerifierAgent` and `run_producer_verifier_pattern()` demonstrate
    independent verification.
- `demo.py` runs router, parallel, verifier, and escalation examples.
- `test_patterns.py` verifies routing, handoffs, fan-out, verification, and
  escalation behavior.

## Real production considerations and trade-offs

- Add deadlines to every specialist call. The final workflow should know
  whether to wait, merge partial results, retry, or escalate.
- Version handoff contracts. A downstream agent or service can break when a
  field changes even if prompts still look plausible.
- Trace each agent separately and preserve parent-child relationships between
  the coordinator and specialists.
- Evaluate pattern choice against a single-agent baseline. Parallel agents can
  improve coverage while increasing cost and operational complexity.
- Keep authorization outside the prompt. Specialist boundaries can reduce tool
  exposure, but service permissions still need enforcement.
- Design explicit conflict handling. Two specialists can both be reasonable and
  still produce incompatible recommendations.

## Practical tips and common mistakes

- Start with coordinator-router before adding agent-to-agent conversation.
- Make handoff payloads smaller than the full conversation.
- Give each specialist a non-overlapping purpose.
- Test routing separately from answer quality.
- Prefer deterministic merge rules for business-critical decisions.
- Escalate on missing evidence, not only on thrown exceptions.
- Avoid creating a specialist for every label in an org chart.
- Do not treat a verifier as independent if it only sees the producer's final
  prose and no source evidence.

## Interview questions

### Basic

- What problem does a coordinator solve in a multi-agent system?
- What information belongs in a handoff record?
- When would a request go to human review?

### Intermediate

- How is parallel specialist fan-out different from sequential delegation?
- Why does merge logic need explicit rules?
- What makes producer-verifier stronger than asking the same agent to check
  itself?

### Advanced

- How would you handle conflicting outputs from two specialists?
- How would you test whether a coordinator is routing correctly?
- How would you migrate a coordinator-router system into a graph workflow?
- What observability fields would you require for production handoffs?

## Commands to install, run, and test

```bash
cd 09_03_common-multi-agent-patterns
python3 -m pip install -r requirements.txt
python3 demo.py
python3 -m pytest
```
