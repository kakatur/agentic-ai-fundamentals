# Understanding Context Windows & Token Budgets

## What Are Context Windows?

Think of a context window as your AI's "working memory" - it's the total amount of text the model can see and process at once. Just like you can't remember every detail from a 500-page book while reading page 450, LLMs have limits on how much they can "remember" in a single conversation.

When we talk about context windows, we're talking about **tokens** - the basic units that LLMs use to process text. A token is roughly 3-4 characters in English. For example:
- "Hello world" = about 2-3 tokens
- "The quick brown fox" = about 4-5 tokens
- One page of text = roughly 400-500 tokens

Context limits are model-specific and change over time. Examples verified on
**June 18, 2026**:

- **GPT-5.5**: 1,050,000-token context window, up to 128,000 output tokens
- **GPT-5.4 mini**: 400,000-token context window, up to 128,000 output tokens
- Current Claude and Gemini models also vary by model and feature; check their
  model cards instead of copying a provider-wide number.

Sources: [OpenAI models](https://developers.openai.com/api/docs/models),
[Claude models](https://platform.claude.com/docs/en/about-claude/models/overview),
and [Gemini models](https://ai.google.dev/gemini-api/docs/models).

The context window includes **everything**: your system prompt, conversation history, function definitions, retrieved documents, and the response the model generates.

## Why Context Windows Matter

Imagine you're building a customer support chatbot. A user has been chatting with your agent for an hour, asking 20 questions. Each exchange adds to the context:
- System prompt: 500 tokens
- Tool definitions: 1,000 tokens
- 20 turns of conversation: 10,000 tokens
- Retrieved knowledge base articles: 5,000 tokens
- **Total: 16,500 tokens**

If your application enforces a 16K request budget, you are already over it.
Depending on the API and framework, the next request may fail validation or
some application layer may truncate input. Do not assume the model provider
will safely remove the right messages for you.

## The "Lost in the Middle" Problem

Here's something fascinating (and frustrating): **LLMs are best at using information at the beginning and end of their context window**. Information in the middle often gets "lost" or ignored.

Researchers found that when you put a crucial fact in the middle of a 10,000-token context, the model might miss it - even though it's technically "in" the context. This is called **positional bias**.

**Practical implications:**
- Put critical instructions at the **start** (system prompt)
- Put the user's current question at the **end**
- Put the most relevant retrieved documents **near the end** or **near the start**
- Less important context can go in the middle (but know it might be ignored)

## Token Budgeting: The Production Challenge

Token budgeting is about **planning how to use your limited context space**. Think of it like RAM in a computer - you have a fixed amount, and you need to allocate it wisely.

### A Typical Token Budget Breakdown

For a RAG-based support agent with an application-level 16K budget:

```
System prompt & instructions:      1,000 tokens  (6%)
Function/tool definitions:         2,000 tokens  (12%)
Retrieved documents:               6,000 tokens  (37%)
Conversation history:              5,000 tokens  (31%)
Current user message:              500 tokens    (3%)
Reserved for response:             2,000 tokens  (12%)
---------------------------------------------------
TOTAL:                            16,500 tokens  (103% - TOO MUCH!)
```

You need to trim somewhere! Options:
1. **Reduce retrieved documents**: Return fewer chunks or summarize them
2. **Compress conversation history**: Keep only last N turns or summarize older ones
3. **Simplify system prompt**: Remove verbose examples
4. **Route to a larger-context model** when quality and cost measurements justify it

### Dynamic Token Budgeting

Smart production systems don't use fixed budgets - they adapt based on what's actually needed:

```python
def calculate_dynamic_budget(
    context_limit: int,
    system_prompt_tokens: int,
    tool_tokens: int,
    user_message_tokens: int,
    reserved_for_response: int = 2000
):
    """
    Dynamically allocate remaining tokens between history and retrieval.
    """
    used = system_prompt_tokens + tool_tokens + user_message_tokens + reserved_for_response
    available = context_limit - used
    
    # Allocate 60% to retrieval, 40% to history (adjust based on your needs)
    retrieval_budget = int(available * 0.6)
    history_budget = int(available * 0.4)
    
    return {
        "retrieval_budget": retrieval_budget,
        "history_budget": history_budget,
        "total_available": available
    }
```

## Counting Tokens Accurately

Rough estimates are useful for planning, but do not use them to enforce a hard
production limit. Count the complete request shape:

- OpenAI provides `client.responses.input_tokens.count(...)`; `tiktoken` remains
  useful for local text estimates.
- Anthropic provides `client.messages.count_tokens(...)`.
- Open-source models commonly expose a tokenizer through their model library.

Images, tools, message wrappers, and provider-added tokens make raw-text counts
insufficient. Prefer the provider's counting API when it is available.

The Anthropic SDK is optional for these examples:

```bash
pip install anthropic
```

## Example Code

See the accompanying code files for:
- `token_counter.py` - Local estimates and provider counting API examples
- `context_manager.py` - Smart context window management with sliding windows
- `token_budget_planner.py` - Dynamic token budget allocation
- `retrieval_truncation.py` - Smart document truncation strategies

## Top Production Challenges & Considerations

### 1. **Context Overflow in Long Conversations**
**Problem**: After 50+ turns, the conversation exceeds your context window.

**Solutions**:
- **Sliding window**: Keep only the last N messages (but preserve the first user message for context)
- **Summarization**: Periodically summarize older messages into a compact "conversation summary"
- **Selective retention**: Keep critical messages (first question, key decisions) and discard small talk

**Trade-off**: Losing context vs. staying within limits. Test which messages can be safely dropped for your use case.

### 2. **Token Counting Inaccuracy**
**Problem**: Your token count doesn't match the API's, causing errors.

**Solutions**:
- Use the provider token-counting endpoint for the complete request
- Add a 5-10% buffer for safety
- Count tokens for **everything**: system prompt, tools, messages, and expected response

**Gotcha**: Tool definitions can be huge! A complex function with many parameters might use 200-500 tokens each.

### 3. **The Lost in the Middle Problem**
**Problem**: Your agent ignores critical information you put in retrieved documents.

**Solutions**:
- Place the most important retrieved chunks at the **end** of context (right before user message)
- Use **explicit references**: "According to the document at the end of this prompt..."
- **Repeat critical facts** in both the system prompt and retrieved context
- Consider **re-ranking** retrieval results and only including top 3-5 documents

**Testing**: Deliberately inject a fact in the middle vs. at the end and see if the model uses it.

### 4. **Cost Explosion with Large Contexts**
**Problem**: Large prompts increase per-request cost and latency. Pricing is
model- and tier-specific and changes frequently.

**Solutions**:
- Use provider-supported prompt caching for repeated static prefixes
- **Compress aggressively**: Summarize documents, remove redundant information
- **Tier your models**: Route routine queries to a suitable lower-cost model and
  use larger or more capable models only when measurements justify it
- **Batch requests**: If processing many similar queries, batch them to reuse context

**Math**: Keep prices in configuration rather than source code:

```python
cost = (
    input_tokens / 1_000_000 * current_input_price
    + output_tokens / 1_000_000 * current_output_price
)
```

Recalculate from the provider's pricing page before publishing estimates.

### 5. **Multi-Turn Context Drift**
**Problem**: As conversations grow, the agent "forgets" the original task or contradicts itself.

**Solutions**:
- **Pin critical context**: Always include the original user goal in every API call
- **Periodic grounding**: Every 5-10 turns, inject a reminder: "Remember, the user's goal is X"
- **Explicit memory system**: Store key facts in a structured memory and inject them as needed
- **Session summarization**: Periodically summarize "what we've accomplished so far"

### 6. **Tool Definition Bloat**
**Problem**: You have 20 tools defined, each with detailed schemas. This uses 5K+ tokens even if only 2 tools are relevant.

**Solutions**:
- **Dynamic tool selection**: Only include tools relevant to the current query (requires a router/classifier)
- **Compressed tool definitions**: Use minimal descriptions, remove examples from schemas
- **Tool categories**: Group related tools and only load the relevant category
- **Tool inheritance**: Define common parameters once, reference them

### 7. **Retrieval Quality vs. Quantity Trade-off**
**Problem**: You can retrieve 50 chunks (15K tokens) or 5 chunks (1.5K tokens). More isn't always better.

**Solutions**:
- **Smart re-ranking**: Use a re-ranker model (Cohere, cross-encoder) to pick the best 5 chunks
- **Hierarchical retrieval**: First get 50 chunks, summarize them, then retrieve the top 5 full chunks
- **Diversity-aware retrieval**: Use MMR (Maximal Marginal Relevance) to avoid redundant chunks
- **Adaptive retrieval**: Retrieve more chunks for complex queries, fewer for simple ones

**Testing**: Track whether increasing chunks from 5 → 10 → 20 actually improves answer quality. Often 10 is the sweet spot.

### 8. **Different Models, Different Tokenizers**
**Problem**: You switch providers or model families and your token counts change.

**Solutions**:
- **Abstract token counting**: Create a `TokenCounter` interface that swaps tokenizers based on model
- **Provider-specific buffers**: derive buffers from observed count differences;
  do not assume one provider always produces more tokens
- **Test with real APIs**: Don't rely on local token counting alone - verify with actual API calls

### 9. **Streaming and Token Budgets**
**Problem**: In streaming mode, you don't know the final token count until the stream completes.

**Solutions**:
- **Estimate response size**: Use historical averages (e.g., "responses are typically 300-500 tokens")
- **Set `max_tokens` parameter**: Explicitly cap the response to ensure it fits your budget
- **Monitor and adjust**: Track actual response sizes and adjust your estimates

### 10. **Context Window Utilization Metrics**
**Problem**: You're using a 200K context model but only filling 10K. You're paying for capacity you don't use.

**Solutions**:
- **Log context usage**: Track min/avg/max/p95 context sizes in production
- **Right-size your model**: If p95 usage is 30K tokens, you don't need a 200K model
- **A/B test model tiers**: Compare quality, latency, and cost for your workload
- **Usage-based routing**: Route small contexts to cheaper models, large contexts to expensive ones

**Key metrics to track**:
- Average tokens per request (input + output)
- P95/P99 token usage (catch outliers)
- Context utilization % (used / available)
- Token cost per request
- Requests that hit context limits

## Interview Questions

### Basic Level

**Q1: What is a context window and why does it matter?**
> **A**: A context window is the maximum amount of text (measured in tokens) that an LLM can process in a single request. It matters because it limits how much conversation history, retrieved documents, and instructions you can include. If you exceed the context window, the request will fail or older content will be truncated, causing the agent to "forget" important information.

**Q2: Roughly how many tokens are in a page of text?**
> **A**: Approximately 400-500 tokens per page. A token is roughly 3-4 characters in English. So a 100-page document would be around 40,000-50,000 tokens.

**Q3: What is the "lost in the middle" problem?**
> **A**: The "lost in the middle" problem refers to LLMs' tendency to better attend to information at the beginning and end of their context window while sometimes ignoring or "losing" information placed in the middle. This means you should place critical instructions at the start and the most relevant retrieved documents near the end.

### Intermediate Level

**Q4: How would you handle a conversation that exceeds your model's context window?**
> **A**: Several strategies:
> 1. **Sliding window**: Keep only the last N messages and drop older ones
> 2. **Summarization**: Periodically compress older messages into a summary
> 3. **Selective retention**: Keep critical messages (first user query, key decisions) and drop less important ones
> 4. **Hierarchical storage**: Move old context to a vector store and retrieve it only when relevant
> 5. **Route selectively**: Use a larger-context model for requests that genuinely need it
> The best approach depends on your use case - customer support might prioritize recent context, while research agents might need to maintain more history.

**Q5: Why is accurate token counting important, and how do you do it?**
> **A**: Accurate token counting is critical because:
> - Prevents errors from exceeding context limits
> - Enables cost prediction and optimization
> - Allows proper budget allocation between history, retrieval, and tools
> 
> Different models use different tokenizers, so you must use the official one:
> - OpenAI: `client.responses.input_tokens.count(...)` for complete request
>   counts; `tiktoken` for local text estimates
> - Anthropic: `client.messages.count_tokens(...)`
> - Never estimate - "words * 1.3" is too inaccurate
> Always add a 5-10% buffer for safety since there can be small variations.

**Q6: You have 16K context and need to fit: 1K system prompt, 2K tools, 5K conversation history, 10K retrieved docs, and 2K for response. What do you do?**
> **A**: This totals 20K tokens, which exceeds the 16K limit. Strategies:
> 1. **Trim retrieval**: Reduce retrieved docs from 10K to 6K (use better re-ranking or fewer chunks)
> 2. **Compress history**: Summarize older conversation turns to reduce 5K → 3K
> 3. **Optimize tools**: Only include relevant tools dynamically, reducing 2K → 1K
> 4. **Reduce response budget**: If queries are typically short answers, reduce 2K → 1K
> 5. **Route to another model**: only after checking current model limits,
>    quality, latency, and pricing
> 
> The right choice depends on what's most critical for your use case. For a support bot, recent history is crucial. For a research agent, retrieved docs matter most.

### Advanced Level

**Q7: How would you implement dynamic token budgeting that adapts based on query complexity?**
> **A**: A sophisticated approach:
> ```python
> 1. Query classification:
>    - Classify query as simple/medium/complex
>    - Simple: "What's your return policy?" → needs minimal retrieval
>    - Complex: "Compare your return policy to competitors and explain differences" → needs lots of retrieval
> 
> 2. Budget allocation matrix:
>    Simple: 70% history, 30% retrieval (user wants conversational continuity)
>    Medium: 50% history, 50% retrieval (balance)
>    Complex: 30% history, 70% retrieval (need comprehensive information)
> 
> 3. Adaptive retrieval:
>    - Simple: Retrieve 3 chunks
>    - Medium: Retrieve 7 chunks
>    - Complex: Retrieve 15 chunks, use re-ranking
> 
> 4. History compression:
>    - If history exceeds budget, summarize older turns
>    - Always preserve the last 2-3 exchanges (recent context critical)
> 
> 5. Monitoring:
>    - Track if complex queries get better answers with more retrieval
>    - A/B test different budget allocations
>    - Watch for queries that hit context limits
> ```
> This requires a query classifier (can be a simple LLM call or fine-tuned model) and careful monitoring to tune the thresholds.

**Q8: Your production system uses a large-context model but P95 input usage is only 15K tokens. How would you optimize this?**
> **A**: This is a significant cost optimization opportunity:
> 
> 1. **Right-size the model**:
>    - Identify current candidate models that safely fit the P95 workload
>    - Compare quality, latency, and current token prices; context capacity alone
>      does not determine price
> 
> 2. **Implement smart routing**:
>    ```python
>    def route_to_model(estimated_tokens):
>        if estimated_tokens < SMALL_MODEL_SAFE_LIMIT:
>            return SMALL_MODEL
>        else:
>            return LARGE_CONTEXT_MODEL
>    ```
> 
> 3. **Pre-flight token estimation**:
>    - Count system prompt + tools + history + estimated retrieval
>    - Route before the expensive API call
> 
> 4. **Graceful fallback**:
>    - If the smaller route rejects the request, retry with the configured
>      larger-context model when the operation is safe to retry
>    - This handles the 5% of outliers
> 
> 5. **Cost analysis**:
>    - Compute savings using observed token counts and current provider pricing
> 
> 6. **Quality monitoring**:
>    - Ensure answer quality doesn't degrade with the smaller context
>    - A/B test a sample of requests between models
> 
> This is a common optimization in production systems - most queries don't need massive context.

**Q9: Explain how you would implement and test a solution to the "lost in the middle" problem for a RAG system.**
> **A**: Comprehensive approach:
> 
> 1. **Position-aware retrieval strategy**:
>    ```python
>    def arrange_context(chunks):
>        # Sort by relevance score
>        sorted_chunks = sort_by_relevance(chunks)
>        
>        # Most relevant: place at the END (nearest to user query)
>        most_relevant = sorted_chunks[:3]
>        
>        # Medium relevance: place at the START
>        medium_relevant = sorted_chunks[3:6]
>        
>        # Lower relevance: skip or place in middle (will be ignored anyway)
>        
>        # Arrange: [medium, ..., most_relevant, user_query]
>        return medium_relevant + most_relevant
>    ```
> 
> 2. **Explicit referencing**:
>    - Add markers: "The following documents are ordered by relevance..."
>    - Reference positions: "In the last document provided..."
>    - Use XML tags: `<most_relevant>`, `<supporting_context>`
> 
> 3. **Testing methodology**:
>    ```python
>    # Needle-in-haystack test
>    def test_position_bias():
>        fact = "The capital of Xinjiang is Urumqi"
>        positions = ["start", "middle", "end"]
>        
>        for pos in positions:
>            context = insert_at_position(fact, pos, haystack_docs)
>            response = llm.complete(
>                context=context,
>                query="What is the capital of Xinjiang?"
>            )
>            accuracy = "Urumqi" in response
>            print(f"Position: {pos}, Accuracy: {accuracy}")
>    ```
> 
> 4. **A/B testing in production**:
>    - Variant A: Documents in relevance order (most → least)
>    - Variant B: Documents in reverse order (least → most)
>    - Variant C: Most relevant at end, medium at start (recommended)
>    - Measure: Answer accuracy, user satisfaction, tool call success
> 
> 5. **Monitoring**:
>    - Track which retrieved chunks are actually cited in responses
>    - If chunks in the middle are never cited, stop including them
>    - Use attention visualization tools (if available) to see where the model focuses
> 
> This problem is subtle and model-dependent, so test with your exact model,
> prompt shape, and context length.

**Q10: Design a token budget monitoring and alerting system for a production agent application.**
> **A**: Complete observability system:
> 
> ```python
> # 1. Instrumentation
> @trace_tokens
> def agent_request(user_message):
>     tokens = {
>         "system_prompt": count_tokens(system_prompt),
>         "tools": count_tokens(tool_definitions),
>         "history": count_tokens(conversation_history),
>         "retrieval": count_tokens(retrieved_docs),
>         "user_message": count_tokens(user_message),
>         "response": 0,  # filled after completion
>         "total_input": 0,
>         "total_output": 0,
>         "context_limit": MODEL_CONTEXT_LIMIT,
>         "utilization_pct": 0
>     }
>     
>     response = llm.complete(...)
>     
>     tokens["response"] = count_tokens(response)
>     tokens["total_input"] = sum([tokens[k] for k in 
>         ["system_prompt", "tools", "history", "retrieval", "user_message"]])
>     tokens["total_output"] = tokens["response"]
>     tokens["utilization_pct"] = (tokens["total_input"] / tokens["context_limit"]) * 100
>     
>     # Log to observability system
>     metrics.record("agent.tokens", tokens)
>     
>     return response
> 
> # 2. Key metrics to track
> - avg_tokens_per_request (input + output)
> - p50, p95, p99 token usage
> - context_utilization_pct (used / limit)
> - tokens_by_component (system, tools, history, retrieval)
> - cost_per_request (tokens * model pricing)
> - requests_exceeding_threshold (e.g., >80% context)
> 
> # 3. Alerting rules
> alerts = [
>     {
>         "name": "High context utilization",
>         "condition": "p95(context_utilization_pct) > 85%",
>         "action": "Consider compression or model upgrade"
>     },
>     {
>         "name": "Context limit breaches",
>         "condition": "count(context_overflow_errors) > 10/hour",
>         "action": "Implement aggressive compression"
>     },
>     {
>         "name": "Cost spike",
>         "condition": "avg(cost_per_request) > 2x baseline",
>         "action": "Investigate token bloat"
>     },
>     {
>         "name": "Inefficient context usage",
>         "condition": "avg(retrieval_tokens) > 10K but p95(utilization) < 30%",
>         "action": "Reduce retrieval, over-fetching"
>     }
> ]
> 
> # 4. Dashboard views
> dashboards = {
>     "Real-time": ["requests/min", "avg_tokens", "errors"],
>     "Cost": ["cost_per_request", "daily_spend", "cost_by_component"],
>     "Efficiency": ["context_utilization", "tokens_by_component", "wasted_capacity"],
>     "Quality": ["response_tokens", "retrieval_utilization", "tool_call_success"]
> }
> 
> # 5. Automated optimization triggers
> if p95_utilization > 90%:
>     enable_aggressive_compression()
> elif p95_utilization < 40% and using_large_context_model:
>     suggest_model_downgrade()
> 
> if avg_retrieval_tokens > 15K and citation_rate < 30%:
>     reduce_retrieval_chunks()  # Fetching more than we use
> ```
> 
> This system provides:
> - Visibility into token usage patterns
> - Early warning of context limit issues
> - Cost optimization opportunities
> - Quality vs. efficiency trade-offs
> - Data-driven tuning of budgets
> 
> In production at scale, this saves significant cost and prevents outages from context overflows.

## Run the Examples

```bash
cd 08_01_context-windows-token-budgets
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python demo.py
pytest -q
```

Use [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for implementation checklists and
[DIAGRAMS.md](DIAGRAMS.md) for visual explanations.
