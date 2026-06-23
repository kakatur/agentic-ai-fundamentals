# When to Use Multi-Agent Systems (And When Not To)

A multi-agent system is not automatically more capable than one well-designed
agent. It distributes context, tools, and control across multiple model-driven
loops, which can unlock parallel work and specialization—but also creates
handoffs, duplicated context, additional cost, and more failure modes.

The durable design rule is:

> Start with the simplest architecture that can meet the requirement. Add
> agents only when measured limitations justify distributing control.

This lesson provides a runnable decision framework for choosing among:

1. Deterministic software
2. One agent with tools
3. Multiple coordinated agents

The guidance was reviewed against primary vendor documentation on **June 23,
2026**:

- [OpenAI: A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)
- [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [LangChain multi-agent overview](https://docs.langchain.com/oss/python/langchain/multi-agent)

## Core concepts and mental model

### Three architecture levels

Do not begin the decision with “Which multi-agent framework should we use?”
Begin with “Where is model judgment actually required?”

```text
Can stable rules handle the task?
  ├─ yes → deterministic workflow
  └─ no
      │
      ▼
Can one agent with clear tools meet the target?
  ├─ yes → single agent with tools
  └─ no, with measured evidence
      │
      ▼
Would separate contexts or control loops fix the limitation?
  ├─ yes → multi-agent candidate
  └─ no  → improve tools, context, model, or workflow first
```

#### Deterministic workflow

Use ordinary software when inputs, transformations, and decisions can be
specified reliably with code or rules.

Examples:

- Export invoices every night.
- Validate a JSON document against a schema.
- Calculate shipping from a published rate table.
- Retry an API call with bounded exponential backoff.

Adding an LLM here usually reduces predictability without solving a real
problem.

#### Single agent with tools

Use one agent when the task benefits from model judgment over changing,
ambiguous, or unstructured input, but one control loop can still select the
right tools and retain the necessary context.

Examples:

- A support assistant that searches policy and creates a ticket.
- A coding agent working in one repository.
- A document analyst that extracts facts and drafts a response.

One agent keeps evaluation, tracing, state, and user interaction comparatively
simple. Tool selection can also be dynamic: the system does not need to expose
every tool and every document on every turn.

#### Multi-agent system

Use multiple agents when separate model-driven control loops create a concrete
advantage that cannot be achieved as cleanly with one agent.

Examples:

- A research lead delegates independent markets to parallel researchers.
- A coordinator isolates legal, security, and financial contexts and tools.
- A producer creates an artifact while an independently prompted verifier
  checks it against a rubric.
- Capabilities are owned and deployed by separate teams with explicit
  contracts.

The important distinction is not the number of prompts. A system with one
agent loading different prompt templates is still one control loop. A
multi-agent system has multiple model-driven loops that can independently
decide what to do next.

### Evidence that can justify multiple agents

Treat the following as evidence, not a checklist that must always be completed.

#### 1. Independent parallel work

The task contains multiple branches that can make progress without repeatedly
waiting on each other.

Good fit:

```text
                     ┌─> research market A ─┐
request ─> planner ──┼─> research market B ─┼─> synthesize
                     └─> research market C ─┘
```

Poor fit:

```text
step A ─> step B ─> step C ─> step D
```

Four agent names do not make a sequential workflow parallel.

#### 2. Context isolation

Specialists require large, mostly distinct bodies of instructions, documents,
history, or tool results. Separate contexts can prevent irrelevant information
from competing for attention.

The handoff should pass the smallest sufficient task contract:

```text
objective + relevant context + constraints + expected output
```

Copying the complete conversation into every agent defeats much of the
isolation benefit.

#### 3. Tool, permission, or ownership boundaries

Separate agents may be useful when capabilities have genuinely different:

- Tool sets
- Credentials and permissions
- Safety policies
- Deployment cycles
- Team ownership

Do not use agents as a substitute for actual authorization. Enforcement still
belongs in tool and service boundaries.

#### 4. Persistent tool-selection failure

A single agent may struggle when tools have overlapping purposes or similar
descriptions. Before splitting the agent:

1. Improve tool names and descriptions.
2. Make parameters distinct and constrained.
3. Hide irrelevant tools dynamically.
4. Add tool-selection evaluations.

Only then treat persistent confusion as evidence for specialization. Tool count
alone is not a reliable threshold.

#### 5. Independent verification

A separate verifier can provide value when independence is part of the design:

- It receives a clear rubric.
- It can inspect the original evidence.
- It is not forced to accept the producer's reasoning.
- Its result changes the workflow through acceptance, rejection, or escalation.

Calling the same prompt twice is not automatically meaningful verification.
Correlated model errors can survive both calls.

## Important design implications

### Coordination is a tax

Every agent boundary adds a protocol:

- What context crosses the boundary?
- Who owns the next action?
- What output schema is required?
- What happens on timeout or partial failure?
- Can the operation be retried safely?
- How is the full path traced?

An architecture diagram with more boxes can look modular while the runtime
becomes less reliable.

### Parallelism improves latency only when work is independent

Parallel agents can reduce wall-clock time for independent branches. They also
increase concurrent model and tool usage. The slowest required branch still
controls join latency, and rate limits can erase the expected gain.

Measure:

- End-to-end latency, including the coordinator
- Total model input and output
- Tool calls and external API cost
- Rate-limit and retry behavior
- Quality at equal cost, not only maximum quality

Anthropic reported strong gains for its breadth-first research workload, while
also reporting substantially higher token use (about 4× for basic agents vs.
chat, 15× for multi-agent research) and warning that tightly coupled domains
are a poor fit. That is evidence for one workload, not a universal multi-agent
performance law.

**Example cost comparison** (GPT-4 Turbo at $0.01/1K input, $0.03/1K output):

| Architecture | Tokens In | Tokens Out | Cost | Quality | Use Case |
|---|---|---|---|---|---|
| Single agent | 8K | 2K | $0.14 | Good | Policy lookup with ticket creation |
| Multi-agent (3 specialists) | 24K | 6K | $0.42 | Better | Cross-domain compliance review (legal, security, finance) |
| Multi-agent (5 parallel researchers) | 60K | 15K | $1.05 | Best | Market research covering 5 independent regions |

A $5,000 consulting engagement may justify $50 in model costs for comprehensive
research. A $0.50 support ticket does not justify $5 in multi-agent
orchestration. Multi-agent design is an economic decision as well as a
technical one.

### Context isolation and information loss trade off

Separate contexts reduce distraction, but handoffs compress information.
Important evidence can be omitted, distorted, or repeatedly summarized.

Prefer durable artifacts for substantial outputs:

```text
specialist writes report.json
specialist returns artifact reference + short summary
coordinator reads the artifact when needed
```

This avoids passing a large result through several lossy conversational
handoffs.

### Failure probability compounds

If a workflow requires several fallible steps, overall success depends on all
required steps and their coordination. More agents create more places for:

- Invalid output
- Timeout
- Duplicate work
- Conflicting conclusions
- Lost context
- Unsafe repeated side effects

Use bounded retries, idempotency keys, checkpoints, timeouts, and explicit stop
conditions. Never allow agents to create agents without resource limits.

### Evaluate the architecture, not the story it tells

Multi-agent traces can sound convincing while doing redundant or unnecessary
work. Evaluate:

- Final task success
- Required intermediate state changes
- Coverage and factual support
- Tool correctness
- Handoff validity
- Latency and cost
- Recovery from partial failure

Always compare against a single-agent baseline. A multi-agent system has not
earned its complexity if it does not improve the metric that matters.

### Use an incremental migration path

```text
deterministic workflow
        ↓ when judgment is required
single agent + clear tools
        ↓ when context is too broad
single agent + dynamic tools/context
        ↓ when measured failures remain
specialized agents behind explicit contracts
        ↓ only when needed
parallelism, handoffs, and independent verification
```

This path preserves a working baseline and makes the reason for each added
boundary testable.

## Code map and implementation guidance

### `architecture_decision.py`

Defines three architecture recommendations:

```python
class Architecture(StrEnum):
    DETERMINISTIC = "deterministic_workflow"
    SINGLE_AGENT = "single_agent_with_tools"
    MULTI_AGENT = "multi_agent"
```

`UseCase` records architectural evidence. It intentionally avoids framework
names and model names:

```python
UseCase(
    name="Cross-market due-diligence report",
    ambiguous_judgment=True,
    changing_or_unstructured_input=True,
    stable_rules_cover_task=False,
    independent_parallel_branches=4,
    needs_context_isolation=True,
    needs_independent_verification=True,
    task_value_supports_extra_cost=True,
)
```

`recommend_architecture()` applies an ordered policy:

1. Prefer deterministic software when stable rules cover the task.
2. Otherwise default to one agent.
3. Recommend multiple agents only when at least two concrete benefits exist,
   the task value supports the extra cost, and coordination penalties are
   limited.

The “two signals” rule is a teaching policy, not an industry standard. Replace
it with thresholds derived from your evaluations and economics.

### `demo.py`

Runs three contrasting scenarios:

- Nightly invoice export → deterministic workflow
- Customer support assistant → single agent with tools
- Cross-market due diligence → multi-agent

### `test_architecture_decision.py`

Tests the important negative cases as well as the positive one:

- Stable rules do not need an agent.
- One multi-agent signal is insufficient.
- Low-value work does not justify extra orchestration.
- Several coordination penalties can outweigh apparent specialization.

These tests protect the bias toward the simplest sufficient architecture.

## Real production considerations and trade-offs

### Establish a baseline before decomposition

Record the single-agent system's:

- Task success rate
- Tool-selection accuracy
- P50 and P95 latency
- Model and tool cost per task
- Human escalation rate
- Failure recovery rate

Without this baseline, “multi-agent worked better” is not a defensible claim.

### Define agent contracts like service contracts

Each delegated task should specify:

```text
objective
allowed tools and permissions
input schema
relevant context
output schema
deadline and budget
retry policy
failure behavior
```

Reject malformed outputs at the boundary. Do not make the coordinator infer
whether an agent completed its task.

### Bound delegation

Set limits for:

- Maximum agents per run
- Maximum delegation depth
- Maximum model and tool calls
- Maximum elapsed time
- Maximum spend

An unconstrained coordinator can turn one user request into an expensive,
unobservable search tree.

### Make partial failure explicit

Decide whether the system should:

- Fail the entire request
- Return partial results with provenance
- Retry one branch
- Substitute a fallback
- Escalate to a human

The answer depends on the task. A missing market in a brainstorming report is
different from a missing sanctions check.

### Apply least privilege

Give each agent only the tools and credentials required for its role. Enforce
permissions in the called service; prompt instructions are not access control.

### Trace across boundaries

Use a shared run identifier plus per-agent spans. Capture:

- Delegation request
- Context and artifact references
- Tool calls
- Structured result
- Token and latency metrics
- Retry and failure events

Sensitive context still needs redaction and retention controls.

## Interview questions

### Basic

**What is the default architecture for an agentic workflow?**

One agent with well-defined tools, after first ruling out deterministic
software. Multiple agents should solve a measured limitation.

**What makes a system multi-agent?**

It has multiple model-driven control loops that can independently choose
actions. Multiple prompt templates inside one loop do not necessarily make
multiple agents.

**Name three reasons to consider multiple agents.**

Independent parallel work, context isolation, and distinct tool, permission,
or ownership boundaries.

### Intermediate

**Why is tool count alone a weak reason to split an agent?**

Tool ambiguity matters more than a universal count. Clear, distinct tools may
scale well, while a small set of overlapping tools can confuse selection.

**When does parallelism fail to improve latency?**

When branches have dependencies, share bottlenecked tools, hit rate limits, or
must wait for one slow required branch before joining.

**How would you test whether a verifier agent adds value?**

Compare producer-only and producer-verifier systems on a fixed evaluation set.
Measure defect detection, false rejection, final quality, latency, and cost.
Ensure the verifier has independent evidence and a clear rubric.

### Advanced

**How do you decide what context crosses an agent boundary?**

Pass the smallest sufficient contract: objective, relevant evidence,
constraints, and expected output. Store large artifacts durably and pass
references rather than repeatedly summarizing them.

**Why can multi-agent reliability be lower even when each agent is capable?**

Required steps can fail independently, and coordination introduces handoff,
state, timeout, retry, and conflict-resolution failures.

**What evidence would justify migrating from one agent to several?**

Repeated evaluation failures attributable to context interference, persistent
tool confusion, insufficient independent parallelism, missing verification, or
organizational boundaries—and a controlled experiment showing that
decomposition improves the target metric enough to justify its cost.

## Install, run, and test

Python 3.11 or newer is recommended because the example uses `StrEnum`.

```bash
cd 09_01_when-to-use-multi-agent-systems
python3 -m pip install -r requirements.txt
python3 demo.py
python3 -m unittest -v
```
