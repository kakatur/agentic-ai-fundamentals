# 8.1 — Context Windows and Token Budgets

Learner job: decide what fits in the model input, reserve room for the answer,
and protect the facts the agent must not lose.

## Mental Model

The model only sees the text you send with the current request. Treat that text
as a working set for one call: instructions, selected facts, recent history,
tool output, and the user request. Context engineering is the job of choosing,
ordering, and labeling that working set.

Instead of starting with "how large is the window?", start with "what must the
model see right now to answer safely?"

## Budget Workflow

1. Reserve output tokens first.
2. Keep a safety margin for formatting, tool schemas, and hidden wrapper text.
3. Mark non-negotiable facts as pinned.
4. Rank supporting facts by task relevance.
5. Drop low-value history before dropping policies, constraints, or the latest
   user request.

The demo shows this with `ContextItem`, `reserve_response_budget`, and
`build_context`.

## Failure Mode: Losing Important Facts

More input does not mean the model will use every fact equally. The
["Lost in the Middle"](https://arxiv.org/abs/2307.03172) result from Liu et al.
showed that models can use information differently depending on where it appears
in a long context. Keep critical constraints visible instead of burying them
inside a large undifferentiated blob.

Practical mitigation:

- put instructions and critical constraints near clear section boundaries
- label retrieved context by purpose
- keep the newest user request at the end
- trim old or weakly related material before trimming required facts

## Code Tour

`context_budget.py` keeps the example intentionally small:

- `estimate_tokens` is a rough local estimator for examples and tests
- `reserve_response_budget` prevents the prompt from consuming the whole window
- `build_context` selects pinned and high-priority items first
- `edge_load_context` formats critical context before supporting context

Real systems should use the tokenizer for the target model. The shape of the
logic stays the same.

## Design Decisions

Pinning is a contract, not a preference. A pinned item should be something the
agent cannot safely answer without.

Priority is task-relative. A fact that matters for billing may be irrelevant for
technical support.

Log dropped context decisions. If a user reports a wrong answer, you need to
know what the model did not see.

## Interview Questions

Basic: What is a context window, and why should you reserve output tokens?

Intermediate: How would you decide which conversation turns to drop first?

Advanced: How would you test whether your prompt layout is vulnerable to losing
critical facts in the middle of a long context?

## Commands

```bash
pip install -r requirements.txt
python demo.py
pytest
```
