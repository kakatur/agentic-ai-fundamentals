# LangGraph Nodes, Edges, And State

LangGraph is easiest to learn when you separate the graph concepts from model
behavior. A graph workflow has state, nodes that update that state, edges that
choose the next node, and reducers that decide how multiple updates are merged.

This lesson uses a deterministic Python graph runner to make those mechanics
visible. The implementation mirrors LangGraph's mental model without requiring
LLM calls, API keys, or a framework dependency.

## Core concepts and mental model

### State is the shared contract

State is the data structure every node reads and updates. In LangGraph, state is
usually defined with a schema such as `TypedDict`, Pydantic, or a dataclass. In
this lesson, `SupportState` carries the request, selected route, retrieved
facts, draft response, risk score, final answer, and execution history.

Good state is explicit. Avoid hiding important workflow decisions inside a
conversation transcript when they should be typed fields:

```text
request -> route -> facts -> draft -> risk -> final_answer
```

### Nodes do work

A node is a function that receives the current state and returns a partial
update. Nodes should have clear ownership:

- classify the request
- retrieve policy facts
- draft a response
- review risk
- finalize or escalate

The node should not secretly decide the whole graph. Keep business logic local
to the node's responsibility, then let edges control flow.

### Edges define flow

Normal edges connect one node to the next:

```text
classify -> retrieve_policy -> draft_response -> review_risk
```

Conditional edges choose among branches after a node runs:

```text
review_risk -- finish --> finalize
review_risk -- escalate --> escalate
```

That separation matters. A node can compute `risk`, while the conditional edge
can decide whether that risk continues to a final answer or a human review path.

### Reducers merge updates

Some fields should be overwritten, and some should be accumulated. The lesson's
`merge_state()` function overwrites scalar fields such as `route`, `draft`,
`risk`, and `final_answer`, but appends tuple fields such as `facts` and
`history`.

In LangGraph terms, append behavior is a reducer. Reducers prevent later nodes
from accidentally deleting useful evidence from earlier nodes.

### Compile before invoke

A graph definition is a plan. A compiled graph is the executable object. This
lesson follows the same discipline: build the graph, compile it, then invoke it
with initial state.

## Important design implications

### Graphs make control flow inspectable

When every step is a named node, the visited path becomes evidence:

```text
classify -> retrieve_policy -> draft_response -> review_risk -> finalize
```

That is easier to debug than a single prompt that internally decides what it
did. Tests can assert the path, the final state, and the branch behavior.

### State design is product design

If `risk` is a first-class field, the system can branch on it, log it, test it,
and expose it to reviewers. If risk only appears inside generated prose, every
downstream step has to rediscover it.

The same applies to route, facts, tool outputs, citations, confidence, cost,
approval status, and retry counts. Put fields in state when later nodes or
operators need them.

### Conditional edges should be boring

Conditional routing should be easy to explain:

- `risk >= 2` escalates
- billing language selects billing policy
- missing required evidence routes to review

If a branch condition is a large hidden prompt, treat it as a classifier node
that writes a typed decision into state. Then use a small conditional edge to
route from that decision.

### Reducers are safety rails

Reducers are important when multiple nodes can contribute to the same field. An
append reducer keeps all facts. A max reducer can preserve the highest severity.
A set union reducer can combine unique flags.

Without a reducer, the last writer wins. That is sometimes correct, but it is a
dangerous default for evidence, history, citations, and warnings.

## Code map and implementation guidance

- `graph_workflow.py`
  - `SupportState` defines the shared state.
  - `NodeResult` defines partial node updates.
  - `StateGraph` registers nodes, normal edges, and conditional edges.
  - `CompiledGraph.invoke()` runs the graph until `END` or a step limit.
  - `merge_state()` demonstrates overwrite versus append reducer behavior.
  - `build_support_graph()` wires a support workflow from classification to
    final answer or escalation.
- `demo.py` runs billing, security, and escalation examples.
- `test_graph_workflow.py` verifies normal flow, conditional flow, reducers,
  compile-time validation, branch errors, and infinite-loop protection.

## Real production considerations and trade-offs

- Prefer typed state over a giant message list. Messages are useful context,
  but typed fields make routing, retries, approval, and reporting testable.
- Name nodes after responsibilities, not implementation details. `review_risk`
  is clearer than `call_model_3`.
- Keep node outputs small. A node should return the fields it owns, not rewrite
  the entire state object.
- Add a maximum step count or recursion limit. Cycles are useful for retry and
  reflection, but unbounded loops are incidents.
- Trace both node execution and state changes. Debugging graph behavior usually
  means asking which node wrote a field and which edge used it.
- Treat conditional edges as control-flow contracts. If branches change, update
  tests and dashboard labels at the same time.
- Use reducers deliberately. Append evidence and history; overwrite fields such
  as the current draft only when replacing the prior value is intended.

## Practical tips and common mistakes

- Start with one straight-line graph before adding loops or parallel branches.
- Make the initial state small and explicit.
- Use one node for classification and one edge for routing.
- Test branch decisions with deterministic inputs.
- Store escalation reasons as state, not only as text in the final answer.
- Avoid node names such as `agent1`, `agent2`, and `processor`.
- Do not let every node mutate every field.
- Do not hide essential decisions inside unstructured model output.

## Interview questions

### Basic

- What is the difference between a node and an edge?
- Why does a graph workflow need shared state?
- What does it mean to compile a graph before invoking it?

### Intermediate

- When should a field be overwritten versus accumulated with a reducer?
- Why is a conditional edge better than burying the next-step decision inside a
  long prompt?
- What should you test first in a graph-based agent workflow?

### Advanced

- How would you design reducers for citations, tool errors, and severity
  scores in a parallel graph?
- What observability fields would you add to debug a graph that sometimes
  takes the wrong branch?
- How would you prevent a retry loop from becoming unbounded while still
  allowing useful recovery?

## Commands

Install the test dependency:

```bash
python3 -m pip install -r requirements.txt
```

Run the demo:

```bash
python3 demo.py
```

Run the tests:

```bash
python3 -m pytest
```
