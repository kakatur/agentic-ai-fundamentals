# Quick Reference: Context Windows & Token Budgets

## Token Counting Cheat Sheet

### Character to Token Ratios
- **English text**: ~4 characters per token
- **Code**: ~2.5-3 characters per token
- **JSON/structured**: ~3 characters per token
- **One page**: ~400-500 tokens

### Example Model Context Limits

Verified June 18, 2026. Recheck model cards before using these values in
production.

| Model | Context Window | ~Pages |
|-------|---------------|--------|
| GPT-5.5 | 1,050,000 tokens | ~2,100-2,600 |
| GPT-5.4 mini | 400,000 tokens | ~800-1,000 |

See [OpenAI models](https://developers.openai.com/api/docs/models),
[Claude models](https://platform.claude.com/docs/en/about-claude/models/overview),
and [Gemini models](https://ai.google.dev/gemini-api/docs/models).

## Quick Token Counting

```python
# OpenAI: exact count for a complete Responses API input
from openai import OpenAI
client = OpenAI()
response = client.responses.input_tokens.count(
    model="gpt-5.5",
    input=text,
)
tokens = response.input_tokens

# OpenAI: local text-only estimate
import tiktoken
encoding = tiktoken.encoding_for_model("gpt-5.4-mini")
tokens = len(encoding.encode(text))

# Anthropic
from anthropic import Anthropic
client = Anthropic()
response = client.messages.count_tokens(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": text}],
)
tokens = response.input_tokens

# Rough estimate (when you can't use official tools)
tokens = len(text) // 4
```

## Context Budget Templates

### Small Application Budget (16K tokens)
```
System prompt:        1,000 tokens  (6%)
Tool definitions:     2,000 tokens  (12%)
Retrieval:            5,000 tokens  (31%)
Conversation history: 5,000 tokens  (31%)
Response budget:      2,000 tokens  (12%)
Safety buffer:        1,384 tokens  (8%)
────────────────────────────────────────
TOTAL:               16,384 tokens  (100%)
```

### Medium Application Budget (128K tokens)
```
System prompt:        2,000 tokens  (1.5%)
Tool definitions:     5,000 tokens  (4%)
Retrieval:           50,000 tokens  (39%)
Conversation history: 50,000 tokens (39%)
Response budget:     15,000 tokens  (12%)
Safety buffer:        6,000 tokens  (4.5%)
────────────────────────────────────────
TOTAL:              128,000 tokens  (100%)
```

### Large Application Budget (200K tokens)
```
System prompt:        2,000 tokens  (1%)
Tool definitions:     5,000 tokens  (2.5%)
Retrieval:           80,000 tokens  (40%)
Conversation history: 90,000 tokens (45%)
Response budget:     20,000 tokens  (10%)
Safety buffer:        3,000 tokens  (1.5%)
────────────────────────────────────────
TOTAL:              200,000 tokens  (100%)
```

## Truncation Decision Tree

```
Need to reduce context?
├─ Need ALL documents represented?
│  └─ Use PROPORTIONAL truncation
│     (trim each document equally)
│
├─ Want only highest quality?
│  └─ Use TOP-N truncation
│     (keep most relevant only)
│
├─ Large context (>10K tokens)?
│  └─ Use POSITION-AWARE truncation
│     (combat "lost in the middle")
│
└─ Documents are redundant?
   └─ Use DIVERSE truncation
      (maximize coverage)
```

## Lost in the Middle - Best Practices

### ✅ DO
- Place critical instructions at the **START** (system prompt)
- Place most relevant docs at the **END** (near user query)
- Place current user question at the **END**
- Use explicit references: "See the document at the end..."

### ❌ DON'T
- Place important information only in the middle
- Assume the model reads everything equally
- Bury critical facts in long documents

## Cost Optimization Rules of Thumb

Pricing, cache discounts, long-context premiums, and service tiers change.
Use the current [OpenAI pricing](https://developers.openai.com/api/docs/pricing)
and the equivalent official page for your provider.

### Quick Cost Calculations
```python
# Prices should come from reviewed configuration.
input_cost = (50_000 / 1_000_000) * input_price_per_million
output_cost = (2_000 / 1_000_000) * output_price_per_million
total_cost = input_cost + output_cost

# At 10K requests/day
daily_cost = total_cost * 10_000
monthly_cost = daily_cost * 30
```

### Cost Reduction Strategies
1. **Use prompt caching** when the provider and request shape support it
2. **Right-size requests and models** using measured quality, latency, and cost
3. **Compress aggressively**: Summarize, deduplicate, truncate
4. **Smart routing**: Simple queries → small models, complex → large models
5. **Batch similar requests**: Reuse context across requests

## Message Format Overhead

Message wrappers, tools, images, and provider-added tokens vary by model and
API shape. Fixed per-message constants are rough teaching estimates only. Use
the provider's token-counting API for preflight validation.

### Example
```python
raw_tokens = sum(local_count(message["content"]) for message in messages)
request_tokens = provider_count(messages=messages, tools=tools)
overhead = request_tokens - raw_tokens
```

## Memory Management Patterns

### Sliding Window
```python
# Keep last N messages
WINDOW_SIZE = 10
history = history[-WINDOW_SIZE:]
```
**Use when**: Conversations are independent, recent context matters most

### Selective Retention
```python
# Keep first N and last M
first_n = history[:2]   # Initial context
last_m = history[-4:]   # Recent context
history = first_n + last_m
```
**Use when**: Initial context is critical, middle is less important

### Summarization
```python
# Summarize old messages
if len(history) > 20:
    summary = llm.summarize(history[:10])
    history = [{"role": "system", "content": summary}] + history[10:]
```
**Use when**: You need to preserve information but reduce tokens

### Preserve Pairs
```python
# Never break Q&A pairs
pairs = [(history[i], history[i+1]) for i in range(0, len(history), 2)]
# Truncate pairs, not individual messages
```
**Use when**: Conversation flow is important

## Monitoring Metrics

### Essential Metrics
```python
metrics = {
    "avg_input_tokens": ...,        # Track average request size
    "avg_output_tokens": ...,       # Track average response size
    "p95_input_tokens": ...,        # Catch outliers
    "p99_input_tokens": ...,        # Catch extreme outliers
    "context_utilization_pct": ..., # Used / available
    "cost_per_request": ...,        # Track spending
    "requests_truncated": ...,      # How often you truncate
}
```

### Alert Thresholds
- **P95 utilization > 85%**: Risk of hitting limits
- **P99 utilization > 95%**: Definitely hitting limits
- **Avg utilization < 40%**: Overprovisioned, use smaller model
- **Cost/request > 2x baseline**: Investigate token bloat

## Common Mistakes to Avoid

1. **❌ Using rough estimates as hard production limits**
   - Different models tokenize differently
   - "Words * 1.3" is NOT accurate

2. **❌ Not accounting for message overhead**
   - Wrappers and tools add model-specific tokens
   - Count the complete request instead of relying on a fixed constant

3. **❌ Ignoring the "lost in the middle" problem**
   - Middle content gets ignored
   - Test your document positioning

4. **❌ Fixed budgets for all queries**
   - Simple queries don't need 10K retrieval
   - Complex queries need more than 2K

5. **❌ Not monitoring actual usage**
   - You can't optimize what you don't measure
   - Track min/avg/max/p95/p99

6. **❌ Forgetting the safety buffer**
   - Always reserve 5-10% for variance
   - Token counts can fluctuate slightly

7. **❌ Using massive context models unnecessarily**
   - Capacity, quality, latency, and token price are separate dimensions
   - Most queries do not benefit from filling a massive context window

## Production Checklist

- [ ] Using provider counting APIs for complete production requests
- [ ] Adding 5-10% safety buffer to calculations
- [ ] Counting message overhead, not just content
- [ ] Testing "lost in the middle" placement strategy
- [ ] Implementing dynamic budget allocation
- [ ] Monitoring p95/p99 token usage
- [ ] Tracking cost per request
- [ ] Testing with maximum conversation lengths
- [ ] Handling context overflow gracefully
- [ ] Logging truncation events for analysis
- [ ] A/B testing truncation strategies
- [ ] Right-sizing model selection based on usage

## Quick Troubleshooting

### Problem: Requests failing with context limit errors
**Solutions**:
1. Add logging to see actual token counts
2. Verify you're using correct tokenizer
3. Check if tool definitions are unexpectedly large
4. Implement aggressive truncation
5. Consider upgrading to larger context model

### Problem: High costs
**Solutions**:
1. Check p95 context utilization
2. If <50%, downgrade to smaller context model
3. Implement prompt caching when supported
4. Reduce retrieval chunks
5. Compress conversation history
6. Route simple queries to cheaper models

### Problem: Poor answer quality after truncation
**Solutions**:
1. Test different truncation strategies
2. Increase retrieval budget for complex queries
3. Use position-aware placement
4. Preserve more conversation history
5. Upgrade to larger context model

### Problem: "Lost in the middle" issues
**Solutions**:
1. Move critical docs to end of context
2. Add explicit references to document positions
3. Use fewer, higher-quality documents
4. Repeat critical information
5. Test with needle-in-haystack benchmarks
