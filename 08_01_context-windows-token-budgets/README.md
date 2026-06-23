# Context Windows and Token Budgets

An agent can have the right tools and the right documents and still fail because
the request was assembled badly. Context engineering is the discipline of
deciding what the model should see now, fitting that information into a bounded
request, and measuring whether the policy works.

By the end of this lesson, you should be able to:

1. Explain which request components compete for context capacity.
2. Reserve output capacity and a safety margin before allocating history and
   retrieval.
3. Choose a deterministic reduction policy for conversation and documents.
4. Assemble, recount, validate, and observe the final request.

## Core concepts and mental model

### The context window is shared capacity

A context window is the model-specific token capacity available to process a
request. Treat it as one shared budget:

```text
instructions
+ tool definitions
+ retrieved evidence
+ conversation state
+ current user input
+ reserved model output
+ safety margin
<= application context budget
```

The advertised model limit is an upper bound, not a target. Filling a large
window can increase latency and cost, and irrelevant context can reduce answer
quality. A production application may intentionally enforce a smaller budget
than the model supports.

### Tokens are not words

A tokenizer converts input into token IDs. A token may be a whole word, part of
a word, punctuation, whitespace, or a fragment of code. Ratios vary across
models, languages, and content types.

Character estimates are useful during planning, but they are not reliable
enough for hard limits. Message structure, tool schemas, images, files, and
provider formatting can add tokens that are absent from the visible text.

For OpenAI Responses requests, the current input-token counting endpoint accepts
the same request shape as the Responses API and includes structural formatting:

```python
from openai import OpenAI

client = OpenAI()
count = client.responses.input_tokens.count(
    model="gpt-5.5",
    instructions="Answer from the supplied evidence.",
    tools=[tool_schema],
    input=messages,
)
print(count.input_tokens)
```

Use local tokenization for fast offline estimates. Use a provider count for
preflight validation when the complete request is near a hard boundary. Record
actual usage after execution.

Source verified June 23, 2026:
[OpenAI token counting](https://developers.openai.com/api/docs/guides/token-counting).
Model names and limits are volatile; recheck provider documentation before
using them in production.

### Budget fixed components before flexible components

Start with components that must fit:

- required instructions and policies
- the current user input
- required tool definitions
- output reservation
- safety margin

Only then allocate the remaining capacity to flexible components such as
conversation history and retrieved documents.

For an application budget of 16,384 tokens:

```text
Application budget                          16,384
Required instructions and tools             -3,000
Current user input                             -500
Reserved model output                       -2,000
Safety margin                                 -819
                                             ------
Available for history and retrieval         10,065
```

This ordering prevents a common failure: trimming history and retrieval, then
discovering that the current input or expected response still cannot fit.

### Context selection is a policy decision

When capacity is scarce, arithmetic cannot decide what matters. The application
needs an explicit policy.

Examples:

- A factual support question may prioritize authoritative retrieval.
- A follow-up question may prioritize recent conversation state.
- A tool-heavy task may load only the relevant tool category.
- A long analysis may reserve more output capacity than a short lookup.

The policy should be deterministic, testable, and visible in metadata. Do not
depend on silent provider truncation to remove the right information.

### Position can affect use

Research on long-context models has shown that information can be used less
reliably when buried in the middle of a long request. This tendency is commonly
called “lost in the middle.”

Treat it as an empirical risk, not a universal rule:

- keep durable instructions in a stable prefix
- keep the current request near the end
- rank and deduplicate retrieval before insertion
- place the strongest supporting evidence close to the question
- test the exact model, prompt shape, and context length used by the application

The primary fix is better selection. Reordering weak evidence does not make it
useful.

## Important design implications

### Preserve semantic units

Truncation should operate on coherent units:

- user and assistant turns
- assistant tool calls and their tool results
- retrieved chunks with source metadata
- structured decisions and unresolved tasks

Dropping arbitrary messages may leave an answer without its question or a tool
result without the call that produced it. A smaller coherent request is usually
better than a larger broken one.

### Separate transcript from memory

A chat transcript records everything that was said. Agent memory should retain
what still matters.

A robust long-running agent often combines:

- pinned user goals and constraints
- structured state for decisions, identifiers, and completed actions
- summaries of older conversation
- a short window of recent verbatim turns
- retrieval from external storage when older details become relevant

Summaries are lossy. Critical facts should be stored structurally or validated
before reuse.

### Select before truncating

For retrieved evidence:

1. rank candidates
2. remove duplicates
3. select for relevance and coverage
4. order the selected chunks
5. enforce the final token limit

Token-exact truncation solves capacity, not relevance. Prefix-cutting a document
can remove the sentence that answers the question.

### Recount the final request

Planning values are estimates. The assembled request is what must fit.

The safe sequence is:

```text
classify task
→ reserve fixed capacity
→ select retrieval
→ compact history
→ assemble exact request
→ count again
→ reduce deterministically or reject
→ execute
→ record actual usage and quality
```

If mandatory components still cannot fit, reject the request, split the task, or
route it explicitly. Silent corruption is not a valid fallback.

## Code map and implementation guidance

### `token_counter.py`

`TokenCounter` demonstrates:

- local OpenAI token estimates through `tiktoken`
- an explicit character fallback when an encoding is unavailable
- optional Anthropic token counting
- estimated message-format overhead

The local methods are deliberately offline-friendly. They do not claim to count
the complete multimodal provider request exactly.

### `token_budget_planner.py`

`TokenBudgetPlanner`:

- classifies a query as simple, medium, or complex
- reserves system, tools, query, response, and a five-percent margin
- allocates the remainder between history and retrieval
- caps allocations to the data actually available
- records utilization statistics

The classifier and average chunk sizes are teaching heuristics. Replace them
with measured distributions and evaluated routing rules in production.

### `context_manager.py`

`ContextManager` demonstrates three history policies:

- sliding window
- complete-pair preservation
- first-plus-recent retention

`build_request()` then:

1. reserves the current message and response capacity
2. formats retrieval before counting it
3. removes duplicate system messages from supplied history
4. truncates conversational history
5. assembles the exact message list
6. recounts the request
7. rejects overflow explicitly
8. returns usage and truncation metadata

### `retrieval_truncation.py`

`RetrievalTruncator` compares:

- top-N packing by relevance
- proportional truncation
- position-aware ordering
- simplified diversity-aware selection

The diversity calculation is intentionally educational. Production systems
should use a meaningful similarity signal, such as embeddings, and evaluate
answer quality end to end.

### `demo.py`

The complete demo shows token estimation, history reduction, dynamic planning,
retrieval selection, final request assembly, and utilization reporting.

## Real production considerations and trade-offs

### Exactness versus availability

A remote counting endpoint is more accurate for a complete request, but it adds
network dependency and latency. Define behavior for count failures:

- proceed with a conservative estimate for clearly small requests
- reject near-limit requests when exact validation is unavailable
- cache counts for stable prefixes and tool schemas where appropriate

### Quality versus token reduction

Lower token usage is not automatically better. Evaluate:

- grounded answer accuracy
- citation correctness
- task completion
- user corrections or escalations
- latency and cost

Compare these measures before and after changing chunk sizes, history windows,
or summarization policies.

### Metrics worth recording

Track by model and request type:

- actual input and output tokens
- reserved versus actual output
- P50, P95, and P99 context utilization
- history messages and retrieval chunks removed
- overflow rejection rate
- latency and cost
- quality after reduction

Log which information was removed without logging sensitive content itself.

### Volatile configuration

Keep model IDs, context limits, output limits, and prices in reviewed
configuration. Date published examples and recheck provider documentation.
Capacity, capability, latency, and price are separate dimensions.

## Interview questions

### Basic

**What competes for a model’s context window?**

Instructions, tools, retrieved evidence, conversation state, current input, and
generated output all consume capacity. Applications should also reserve a
safety margin.

**Why is a character estimate insufficient for a hard limit?**

Tokenization varies by model and content, and the complete request may include
message boundaries, tools, images, files, and provider formatting.

### Intermediate

**A request does not fit. What should be reduced first?**

There is no universal order. Preserve mandatory instructions, current input,
output capacity, and safety margin first. Apply the application’s explicit
policy to flexible history, retrieval, and optional tools.

**Why preserve message pairs or tool-call groups?**

They are semantic units. Splitting them can make the retained context
incoherent even when it fits numerically.

### Advanced

**How would you evaluate a dynamic budget planner?**

Create labeled request classes, compare allocation decisions with quality,
latency, and cost outcomes, and test boundary cases. Replace fixed averages with
observed token distributions.

**How do you diagnose “the agent forgot”?**

Inspect trace metadata to determine whether the information was never
retrieved, removed by compaction, positioned poorly, included but ignored, or
contradicted by later context.

## Install, run, and test

```bash
python3 -m pip install -r requirements.txt
python3 demo.py
python3 -m pytest -q
```

Expected test result:

```text
7 passed
```
