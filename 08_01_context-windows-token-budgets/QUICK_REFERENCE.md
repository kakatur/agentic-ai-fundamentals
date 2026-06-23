# Quick Reference: Context Windows and Token Budgets

## Budget equation

```text
instructions
+ tools
+ retrieval
+ history
+ current input
+ reserved output
+ safety margin
<= application budget
```

Reserve fixed components first. Allocate flexible history and retrieval from
what remains.

## Safe request flow

```text
1. Classify the task.
2. Reserve instructions, current input, output, and margin.
3. Select and deduplicate retrieval.
4. Compact history in semantic units.
5. Assemble the exact request.
6. Count again.
7. Reduce deterministically or reject.
8. Record actual usage and quality.
```

## Counting rules

- Character ratios are planning estimates only.
- Count the formatted request, not isolated text fields.
- Include tools, message structure, images, and files.
- Use provider counting APIs near hard boundaries.
- Record actual input and output usage after execution.

OpenAI Responses example:

```python
count = client.responses.input_tokens.count(
    model="gpt-4-turbo",  # or "gpt-4", "gpt-4o"
    instructions=instructions,
    tools=tools,
    input=input_items,
)
input_tokens = count.input_tokens
```

Last verified: June 23, 2026  
Source: [OpenAI token counting](https://developers.openai.com/api/docs/guides/token-counting).

## History policy chooser

| Need | Policy | Risk |
|---|---|---|
| Recent conversational continuity | Sliding window | Loses early constraints |
| Coherent question/answer turns | Preserve pairs | Simple grouping may miss tool dependencies |
| Original goal plus recent work | First plus recent | Drops middle decisions |
| Long-running task state | Structured summary plus recent turns | Summary drift |

Preserve assistant tool calls with their corresponding tool results.

## Retrieval policy chooser

| Need | Policy | Risk |
|---|---|---|
| Best evidence only | Top-N packing | May reduce source coverage |
| Every source represented | Proportional truncation | Can cut away key sentences |
| Strong evidence near query | Position-aware ordering | Position cannot fix weak evidence |
| Broad, non-redundant coverage | Diversity-aware selection | Requires meaningful similarity |

Select for relevance before enforcing the final numerical limit.

## Overflow policy

```text
Does the final request fit?
├─ Yes → execute and record actual usage
└─ No
   ├─ Remove optional tools
   ├─ Reduce or rerank retrieval
   ├─ Compact older history
   ├─ Split the task
   ├─ Route explicitly
   └─ Reject if mandatory components still do not fit
```

Never rely on silent truncation for correctness-sensitive workflows.

## Lost-in-the-middle checks

- Keep stable instructions near the beginning.
- Keep the current request near the end.
- Place strongest evidence close to the question.
- Test multiple context lengths and evidence positions.
- Repeat tests after changing models or prompt structure.

## Production metrics

```python
metrics = {
    "input_tokens": ...,
    "output_tokens": ...,
    "reserved_output_tokens": ...,
    "context_utilization_pct": ...,
    "history_messages_removed": ...,
    "retrieval_chunks_removed": ...,
    "overflow_rejected": ...,
    "latency_ms": ...,
    "cost": ...,
    "quality_score": ...,
}
```

Review P50, P95, and P99 distributions. Optimize quality, latency, and cost
together.

## Common mistakes

- Counting raw text only.
- Reserving no output capacity.
- Treating the advertised context limit as a utilization target.
- Dropping arbitrary messages instead of semantic units.
- Injecting every retrieved chunk.
- Assuming summaries are lossless.
- Hard-coding model limits and prices.
- Logging truncation counts without recording what policy made the decision.

## Commands

```bash
python3 demo.py
python3 -m pytest -q
```
