# LangGraph Fundamentals: Nodes, Edges & State

LangGraph represents an agent workflow as a graph whose state changes over
time. The graph structure makes control flow explicit: nodes perform work,
edges choose what runs next, and state carries data between steps.

This lesson uses deterministic Python functions rather than an LLM. That keeps
the graph mechanics visible and makes every example runnable without API keys.
Once these mechanics are clear, an LLM call is simply another node
implementation.

The examples were verified against LangGraph **1.2.6 on June 19, 2026**.

Primary references:

- [LangGraph Graph API overview](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [LangGraph Python reference](https://reference.langchain.com/python/langgraph/graphs/)
- [LangGraph releases](https://github.com/langchain-ai/langgraph/releases)

## Core concepts and mental model

### When to use a graph (and when not to)

A graph is useful when your workflow includes:

- **Branching**: Different paths based on runtime decisions
- **Parallel execution**: Independent work that can run concurrently
- **Persistence**: State must survive across process restarts or pauses
- **Human intervention**: Approval, review, or input breaks execution flow
- **Observability**: You need to inspect, debug, or audit the execution path

**When NOT to use a graph**:

- ❌ Linear 3-step ETL: `read → transform → write` is clearer as three functions
- ❌ Single API call + parse: One HTTP request doesn't need graph machinery
- ❌ Simple retry loop: A `for` loop with `try/except` is more direct
- ❌ Pure data transformation: Map/reduce operations don't need state management

**Decision rule**: If you can draw the control flow as a straight line with no
branches, loops, or pauses, use ordinary functions. Reach for a graph when the
topology itself carries meaning.

### Workflow topology

The support workflow demonstrates conditional routing:

```text
START
  │
  ▼
normalize_request
  │
  ▼
assess_risk
  │
  ├── low risk ──> fast_path ──┐
  │                            │
  └── high risk -> review_path ├──> finalize ──> END
                               │
```

The parallel workflow demonstrates fan-out and join:

```text
                       ┌─> research_reliability ─┐
START ─────────────────┤                         ├─> synthesize ─> END
                       └─> research_operations ──┘
```

These structures make execution paths visible. A conditional branch shows where
decisions happen. A join shows where parallel work must complete before
continuing.

### State is the shared snapshot

A `StateGraph` is parameterized by a state schema. A `TypedDict` is the normal
starting point because it documents available channels without adding runtime
validation overhead.

```python
class SupportState(TypedDict):
    request: str
    normalized_request: str
    risk_score: int
    route: Literal["fast_path", "review_path"]
    response: str
    audit_log: Annotated[list[str], operator.add]
```

Each key is a state channel. Nodes read the current snapshot and return updates
for the channels they own. They do not need to return the entire state.

```python
def normalize_request(state: SupportState) -> dict:
    return {
        "normalized_request": " ".join(state["request"].lower().split()),
        "audit_log": ["normalized request"],
    }
```

By default, a new value overwrites the existing value for that channel. The
`audit_log` annotation attaches `operator.add` as its reducer, so new lists are
appended instead.

### Nodes do work

A node is a synchronous or asynchronous function. A node may:

- Transform data.
- Call an LLM or external API.
- Execute a tool.
- Validate policy.
- Prepare a human-review request.
- Emit observability or audit information.

Keep node outputs narrow. A normalization node should update normalized input,
not quietly decide routing, write the final answer, and perform external side
effects. Narrow nodes are easier to test, retry, observe, and replace.

### Edges define control flow

Normal edges represent unconditional transitions:

```python
builder.add_edge(START, "normalize_request")
builder.add_edge("normalize_request", "assess_risk")
```

`START` receives graph input. `END` marks a terminal path. Modern LangGraph
code should express these transitions directly with `add_edge`.

Conditional edges route from current state:

```python
builder.add_conditional_edges(
    "assess_risk",
    route_after_assessment,
    {
        "fast_path": "fast_path",
        "review_path": "review_path",
    },
)
```

The routing function reads state and returns a route key. It should not mutate
state. The preceding node records the routing decision in state so execution
remains explainable after the run.

### Compilation creates the runnable graph

The builder describes topology. Calling `compile()` validates the graph and
produces the runnable object:

```python
graph = builder.compile()
result = graph.invoke(initial_state("I need a refund"))
```

Compilation is also where production features such as checkpointers,
breakpoints, and caches are attached.

### Execution proceeds in super-steps

LangGraph uses a message-passing execution model inspired by Pregel. Nodes
activated together run in the same super-step. Multiple outgoing normal edges
can activate parallel nodes.

The parallel example fans out to two research nodes:

```text
                       ┌─> research_reliability ─┐
START ─────────────────┤                         ├─> synthesize ─> END
                       └─> research_operations ──┘
```

Both branches update `notes` in the same super-step. The reducer makes that
merge legal:

```python
notes: Annotated[list[str], operator.add]
```

The join edge lists both source nodes, so `synthesize` runs after both complete:

```python
builder.add_edge(
    ["research_reliability", "research_operations"],
    "synthesize",
)
```

Without an appropriate reducer, concurrent writes to the same channel are
ambiguous and should be treated as a graph design error.

## Important design implications

### State is an interface, not a dumping ground

State couples nodes. Every extra channel expands the graph's shared contract.
Store data in graph state when downstream steps, persistence, replay, or
inspection require it. Keep transient implementation details local to a node.

Use explicit input and output schemas when callers should not provide or
receive every internal channel.

### Separate state updates from routing

This lesson uses:

- A node to calculate and record risk.
- A conditional edge to choose the branch.

That separation is useful when routing is read-only. LangGraph also provides
`Command` for cases where one node must update state and route atomically.
Avoid adding a static edge from a node that also performs dynamic routing:
both paths can execute.

### Reducers are per-channel merge policies

A reducer answers: "How should this update combine with the existing value?"

- No reducer: overwrite the channel.
- `operator.add`: append lists or add compatible values.
- Custom reducer: implement domain-specific conflict handling.
- `add_messages`: merge message history while respecting message IDs.

Choose reducers based on semantics, not convenience. Appending every event may
produce duplicate data when nodes retry.

### Node boundaries are retry boundaries

With checkpointing, graph state is saved at super-step boundaries. A resumed or
retried node can run again from the beginning. External side effects therefore
need idempotency keys, upserts, or read-before-write protection.

Keep side effects isolated from non-deterministic planning where practical.
For example, generate an operation ID in state before a node charges a card.

### Streaming exposes execution, not just the answer

`invoke()` returns final state. `stream(..., stream_mode="updates")` emits each
node's update:

```python
for update in graph.stream(input_state, stream_mode="updates"):
    print(update)
```

This is valuable for progress UIs, debugging, and tests that assert the route
actually taken rather than only checking the final response.

## Code map and implementation guidance

### `support_workflow.py`

Builds the main graph:

```text
START
  │
  ▼
normalize_request
  │
  ▼
assess_risk
  │
  ├── low risk ──> fast_path ──┐
  │                            │
  └── high risk -> review_path ├──> finalize ──> END
                               │
```

Key lessons:

- `SupportState` defines shared channels.
- Nodes return partial state updates.
- `audit_log` uses a reducer.
- Risk scoring tokenizes text so punctuation does not hide a high-risk term.
- A conditional edge selects exactly one branch.
- Both branches converge on a common finalizer.

### `parallel_workflow.py`

Demonstrates parallel fan-out, reducer-based merging, and a barrier-style join.
The branch output order is not used as business logic; `synthesize` sorts notes
to make the example's final string deterministic.

### `demo.py`

Streams the low-risk and high-risk paths, then invokes the parallel graph.
The output shows node boundaries and accumulated final state.

### `test_workflows.py`

Tests:

- Both conditional routes.
- Preservation of channels across partial updates.
- The exact node path exposed by update streaming.
- Reducer behavior across parallel branches.
- Join behavior before synthesis.

### Failure and retry behavior (not yet implemented)

A production graph should handle node failures explicitly. This lesson uses
deterministic functions, so failures are not demonstrated. In a real workflow:

- A node that raises an exception does not update state.
- The graph execution stops at that node.
- With checkpointing, the workflow can resume from the failed node after a fix.
- Side-effecting nodes (payment, notifications) need idempotency keys to prevent
  duplicate operations on retry.

Example failure handling (not in this lesson's code):

```python
def charge_payment(state: PaymentState) -> dict:
    """Idempotent payment node using operation ID from state."""
    if state.get("payment_completed"):
        return {}  # Already processed, skip
    
    try:
        result = payment_api.charge(
            amount=state["amount"],
            idempotency_key=state["operation_id"]
        )
        return {
            "payment_completed": True,
            "receipt": result.receipt_id,
            "audit_log": [f"charged {state['amount']}"]
        }
    except PaymentError as e:
        return {
            "payment_completed": False,
            "audit_log": [f"payment failed: {e}"]
        }
        # Graph execution stops here; manual intervention or retry needed
```

The operation ID is generated before the payment node runs, making retries safe.

## Production considerations and trade-offs

### Schema selection

- Use `TypedDict` for lightweight static structure.
- Use a dataclass when useful defaults belong in the state model.
- Use Pydantic when runtime validation is worth its additional overhead.
- Separate input, internal, and output schemas when exposing all state would
  create an unstable or unsafe API.

### Routing safety

- Make route values a closed set with `Literal`.
- Map route keys to node names explicitly.
- Ensure every expected route reaches a terminal node or an intentional loop.
- Set recursion limits for cyclic workflows and test exit conditions.
- Do not mix static and dynamic routing from the same source node unless
  parallel execution is intentional.

### Parallel execution

Parallel branches reduce latency only when their work is independent. They can
increase rate-limit pressure, external load, and merge complexity.

For every channel written by parallel nodes:

1. Define a valid reducer.
2. Decide whether update order matters.
3. Test duplicate and retry behavior.
4. Define how partial branch failures are handled.

### Persistence and replay

Add a checkpointer when the workflow must survive process failure, pause for
human input, retain thread state, or support time travel. Treat checkpointed
state as durable application data: version schemas, avoid secrets unless
protected, and plan migrations.

### Observability

Record:

- Node start, completion, latency, and failure.
- Route decisions and the state inputs that justified them.
- Retry counts.
- State size growth.
- External operation IDs.
- Graph and prompt versions.

Avoid logging unrestricted state when it can contain credentials, personal
data, or proprietary documents.

### Testing strategy

Test nodes as ordinary functions first. Then test the compiled graph for:

- Route coverage.
- Terminal behavior.
- Reducer semantics.
- Parallel joins.
- Streaming events.
- Retry and idempotency behavior.
- Schema migration compatibility.

Use deterministic fakes for LLM and tool nodes. A graph test that depends on a
live model is slow, expensive, and difficult to reproduce.

## Interview questions

### Basic

**What are state, nodes, and edges in LangGraph?**

State is the shared workflow snapshot. Nodes read state and return updates.
Edges determine which nodes run next.

**Why must a `StateGraph` be compiled?**

The builder only describes state and topology. Compilation validates the graph
and produces a runnable object; it also attaches runtime capabilities such as
checkpointers and caches.

**Does a node need to return the complete state?**

No. A node normally returns only the channels it changes. LangGraph merges
those updates using each channel's reducer.

### Intermediate

**What happens when a state channel has no reducer?**

Updates overwrite the existing value. A reducer is required when values should
accumulate or when parallel updates need a defined merge policy.

**When should you use a conditional edge instead of `Command`?**

Use a conditional edge for read-only routing based on state. Use `Command` when
a node needs to update state and select the next node in one return value.

**How do parallel branches join?**

Add outgoing edges that activate the branches, define reducers for concurrently
written channels, and use an edge with a list of source nodes when the
downstream node must wait for all listed branches.

### Advanced

**Why must side-effecting nodes be idempotent?**

Checkpointing occurs at graph step boundaries. A retry or resume can execute a
node from its beginning, so an unprotected side effect may happen twice.

**How would you evolve a persisted state schema?**

Version the schema and graph, use additive changes where possible, define
migrations for renamed or retyped channels, test old checkpoints against new
code, and avoid assuming every in-flight thread began on the latest graph.

**What is wrong with adding a static edge to a node that returns
`Command(goto=...)`?**

The static edge still executes. The command adds dynamic routing rather than
replacing existing static topology, so both destinations may run.

## Install, run, and test

From this lesson directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python demo.py
pytest -q
```

Expected test result:

```text
5 passed
```
