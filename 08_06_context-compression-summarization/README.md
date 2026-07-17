# 8.6 — Context Compression and Summarization

Learner job: shrink long context without losing constraints, decisions, or open
tasks.

## What Good Compression Preserves

Compression should protect the facts that change future behavior while removing
details the next call does not need:

- non-negotiable constraints
- decisions already made
- open tasks
- user preferences
- unresolved risks

Lower-value details can become background summary or disappear.

## Compression Workflow

1. Classify the input before summarizing.
2. Pull constraints out into their own section.
3. Preserve decisions and open tasks as explicit facts.
4. Summarize background details last.
5. Test the compressed output against known must-keep facts.

## Implementation Walkthrough

`context_compression.py` uses rule-based classification so the lesson is
deterministic:

- `classify_line` assigns each line a kind
- `compress_context` preserves high-value facts
- `render_compressed_context` keeps constraints outside the summary

The same contract applies when a model writes the summary. Tests should prove
that critical facts survive compression.

## Common Mistakes

Do not ask a model to "summarize everything" without telling it what must be
preserved.

Do not merge constraints into prose where they become easy to miss.

Do not compress away unresolved tasks.

Do not trust compression without regression examples.

## Evaluation Strategy

Build a small set of conversations with known must-keep facts. Compress them,
then assert those facts are still present in structured fields. This catches
many failures before they become user-visible.

## Interview Questions

Basic: Why can summarization be dangerous for agent memory?

Intermediate: What types of information should be preserved outside a free-form
summary?

Advanced: How would you evaluate an LLM-based context compressor before using
it in an agent?

## Commands

```bash
pip install -r requirements.txt
python demo.py
pytest
```
