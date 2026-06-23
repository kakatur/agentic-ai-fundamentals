# Introduction to LLM-Ops

LLM-Ops is the operating discipline for shipping LLM applications without
treating model behavior as a mystery. It connects prompts, models, evaluation
sets, traces, release gates, monitoring, rollback, and governance into one
feedback loop.

This lesson uses deterministic Python instead of a live model. That keeps the
operational loop visible and makes the examples runnable without API keys. The
"model" functions classify support tickets, the eval set defines expected
behavior, traces record what happened, and the release gate decides whether a
candidate prompt can ship.

Primary references:

- [OpenAI evals guide](https://developers.openai.com/api/docs/guides/evals) -
  as of June 23, 2026, OpenAI notes that its Evals platform is being
  deprecated and points new evaluation users toward Datasets for iteration.
- [OpenTelemetry Generative AI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) -
  as of June 23, 2026, the OpenTelemetry docs say GenAI semantic conventions
  have moved to the dedicated OpenTelemetry GenAI semantic conventions
  repository.
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/)

## Core concepts and mental model

### LLM-Ops is a loop, not a dashboard

A useful LLM-Ops loop has five parts:

```text
change -> evaluate -> trace -> decide -> monitor
   ^                                  |
   |                                  v
   +------------- improve / rollback -+
```

The change might be a new model, prompt, retrieval index, tool, policy, or
router. The evaluation checks expected behavior before release. Tracing records
what actually happened during each run. The release gate decides whether the
change is safe enough to promote. Monitoring watches production for drift,
cost, latency, failures, and safety regressions.

If one part is missing, the loop breaks:

- No evals: every prompt edit is a manual vibe check.
- No traces: failures cannot be explained after the fact.
- No release gate: metrics are advisory, not operational.
- No monitoring: production drift is discovered by users.
- No rollback path: a bad release becomes an incident instead of a routine
  revert.

### Evals turn expectations into executable checks

An eval example is a small contract:

```python
EvalExample(
    id="billing-refund",
    ticket="I was charged twice and need a refund.",
    expected_intent="billing",
    expected_severity="high",
    tags=("money", "customer-impact"),
)
```

The example defines the input, the expected output, and tags that explain why
the case matters. Good eval sets include common behavior, edge cases, high-risk
cases, regression examples from production, and adversarial cases when the
application is exposed to untrusted text.

The lesson uses exact-match grading because the task is classification. Other
LLM applications may need structured checks, rubric-based graders, human review,
pairwise comparison, or end-to-end task success metrics. The important rule is
that the grader must match the risk. A casual tone grader is not enough for a
financial approval workflow.

### Traces make behavior inspectable

Each eval run emits a `TraceRecord`:

```python
TraceRecord(
    trace_id=...,
    example_id="billing-refund",
    model_version="support-router",
    prompt_version="triage-v2",
    expected_severity="high",
    actual_severity="normal",
    passed=False,
    ...
)
```

That record links the input case, model version, prompt version, result,
latency, token estimate, and pass/fail outcome. In a real system, the trace
would also connect retrieval calls, tool calls, guardrail decisions, and final
user-visible output.

This is why observability for LLM applications must capture more than HTTP
status and latency. A request can return `200 OK` and still be wrong, unsafe,
too expensive, or routed to the wrong tool.

### Release gates convert metrics into decisions

The candidate in this lesson improves response wording but introduces a
regression: refund requests are no longer treated as high severity. Overall
accuracy drops, and high-severity recall drops even more.

The release report checks:

- Overall accuracy
- Recall for high-severity examples
- Average latency
- Average token usage

Promotion requires every check to pass. This matters because a single aggregate
score can hide the failure you care about most. A model that is 95% accurate
overall may still be unacceptable if it misses the highest-risk 5%.

### Monitoring closes the production loop

Pre-release evals are necessary, but they are not enough. Production inputs
change. Users discover strange phrasing. Retrieval indexes drift. Tool schemas
change. Model behavior can change when you upgrade providers or versions.

Production monitoring should watch at least:

- Quality: task success, escalation rate, user corrections, human review
  outcomes
- Safety: prompt injection attempts, policy violations, unsafe tool requests
- Reliability: errors, timeouts, retries, fallback rates
- Cost: token usage, cache hit rates, tool calls, per-customer spend
- Latency: p50, p95, p99, queue time, provider time
- Drift: input mix, retrieval hit rate, label distribution, unanswered
  categories

The right monitors depend on the product. A coding agent, support chatbot,
medical intake assistant, and invoice processor do not share the same risk
profile.

## Important design implications

### Version the whole behavior surface

Do not version only the model name. The shipped behavior includes:

- Model and provider
- Prompt or instructions
- Tool schemas and permissions
- Retrieval corpus and ranking settings
- Safety policies and guardrails
- Output parsers
- Fallback behavior
- Evaluation set and grading logic

When a trace says `prompt_version="triage-v2"`, it should be possible to
reconstruct what was actually run.

### Keep eval sets representative and uncomfortable

An eval set should not be a trophy case of examples the system already handles.
It should include the cases that make the team nervous:

- Expensive actions
- Sensitive data
- Ambiguous user intent
- Conflicting instructions
- Untrusted retrieved content
- Known production failures
- Long-context and edge-format inputs

Small curated evals are valuable early. Larger datasets become important when
you need confidence across segments, languages, tools, customers, or product
surfaces.

### Separate product metrics from model metrics

Model accuracy is not the same as product success. Product metrics answer
questions such as:

- Did the user finish the task?
- Did the workflow avoid unnecessary escalation?
- Did the system preserve trust when it could not answer?
- Did cost stay inside the business budget?
- Did humans spend less time correcting the system?

Model metrics are inputs to release decisions. Product metrics determine
whether the feature is actually working.

### Prefer layered defenses

OWASP's 2025 LLM risks include prompt injection, sensitive information
disclosure, improper output handling, excessive agency, and unbounded
consumption. LLM-Ops does not replace security work, but it gives security work
a place to run continuously.

Useful controls include:

- Least-privilege tool access
- Human approval for sensitive actions
- Output validation before side effects
- Segregation of untrusted retrieved text from instructions
- Rate limits and budget limits
- Red-team and regression evals
- Audit logs for tool calls and policy decisions

### Treat rollback as a feature

A rollback plan should exist before release. If a candidate fails in
production, the team should know which model, prompt, index, policy, or tool
schema to restore. A system that cannot be rolled back is not production-ready.

## Code map and implementation guidance

### `llmops.py`

Defines the lesson's operational loop.

`EvalExample` stores golden test cases. `TraceRecord` stores observable
runtime behavior. `ReleaseReport` turns traces into a promotion decision.

```python
def run_eval(
    *,
    examples: Iterable[EvalExample],
    model: ModelFn,
    model_version: str,
    prompt_version: str,
) -> tuple[TraceRecord, ...]:
```

`run_eval` is the core loop: run each example, parse the output, compare it to
expected behavior, estimate operational metadata, and emit trace records.

```python
def evaluate_release(
    *,
    traces: tuple[TraceRecord, ...],
    minimum_accuracy: float = 0.90,
    minimum_high_severity_recall: float = 1.0,
    maximum_average_latency_ms: float = 50.0,
    maximum_average_tokens: float = 40.0,
) -> ReleaseReport:
```

`evaluate_release` applies the gate. The defaults are intentionally strict for
high-severity recall because a support router that misses urgent cases should
not ship.

### `demo.py`

Runs the baseline and candidate classifiers, prints release reports, and shows
the failed candidate traces.

The baseline passes. The candidate fails because it downgrades a refund case
from `high` severity to `normal`.

### `test_llmops.py`

Tests the operational behavior:

- The baseline is promoted.
- The candidate regression is blocked.
- Trace records explain the failed case.
- High-severity recall focuses on critical examples.
- Invalid model output is rejected.

## Real production considerations and trade-offs

### Exact-match graders are simple but narrow

Exact-match grading works well for classification, routing, and structured
labels. It is too brittle for open-ended writing or multi-step tool use. Use
the simplest grader that measures the real requirement, but do not pretend a
simple grader covers behavior it cannot see.

### LLM-as-judge can scale review but adds another model risk

LLM graders are useful for style, policy, relevance, and nuanced quality. They
also need calibration. Track judge agreement with humans, keep judge prompts
versioned, and periodically review false positives and false negatives.

### Production data is useful but sensitive

Real failures make excellent evals. They may also contain private data. Build a
process for redaction, consent, retention, and access control before copying
production examples into test datasets.

### Observability has privacy costs

Traces can contain prompts, retrieved documents, tool arguments, and model
outputs. Log enough to debug and audit, but avoid collecting secrets by
default. Apply redaction before storage, and control access to raw traces.

### The release gate should match the blast radius

A low-risk internal summarizer might use a small curated eval and manual
review. A customer-facing agent with payment tools needs stricter gates,
security testing, approval workflows, monitoring, and rollback drills.

## Interview questions

### Basic

1. What problem does LLM-Ops solve that ordinary application logging does not?
2. Why should prompts, models, and tool schemas all be versioned?
3. What is a golden eval example?
4. Why can an LLM request return `200 OK` and still be a production failure?
5. What is the difference between an eval and a production monitor?

### Intermediate

1. How would you design an eval set for a customer support agent?
2. When is exact-match grading appropriate, and when is it too brittle?
3. Why might high-severity recall matter more than overall accuracy?
4. What should an LLM trace capture for a tool-using agent?
5. How would you safely add production failures back into an eval set?

### Advanced

1. How would you detect prompt or retrieval drift in production?
2. How would you evaluate an agent whose success depends on multiple tool
   calls and partial progress?
3. What are the privacy risks of storing full prompts and completions in trace
   logs?
4. How would you design release gates for a feature with different customer
   risk tiers?
5. How would you combine human review, automated graders, and production
   telemetry into one improvement loop?

## Commands

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the demo:

```bash
python3 demo.py
```

Run tests:

```bash
python3 -m pytest
```
