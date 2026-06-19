"""
Complete Demo - Context Windows & Token Budgets

This script demonstrates all the concepts covered in this module:
1. Token counting across different providers
2. Context management with sliding windows
3. Dynamic token budget planning
4. Smart retrieval truncation strategies
"""

from token_counter import TokenCounter, estimate_page_tokens
from context_manager import ContextManager
from token_budget_planner import TokenBudgetPlanner
from retrieval_truncation import RetrievalTruncator


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_token_counting():
    """Demo 1: Token Counting"""
    print_section("DEMO 1: Token Counting Across Providers")

    counter = TokenCounter()

    # Sample texts
    short_text = "Hello, how are you?"
    medium_text = "Artificial intelligence and machine learning are transforming software development."
    long_text = """
    Large language models have changed how we build applications.
    These models can understand context, generate human-like text, and even write code.
    However, they have limitations including context windows, token budgets, and costs.
    Understanding these constraints is crucial for building production-ready AI agents.
    """ * 5

    print("1.1 Basic Token Counting:")
    print(f"   Short text: '{short_text}'")
    print(f"   OpenAI local estimate: {counter.count_openai_tokens(short_text, 'gpt-5.4-mini')}")
    print(f"   Anthropic tokens: {counter.count_anthropic_tokens(short_text)}")

    print("\n1.2 Comparing Text Lengths:")
    for label, text in [("Medium", medium_text), ("Long", long_text)]:
        openai_tokens = counter.count_openai_tokens(text, 'gpt-5.4-mini')
        chars = len(text)
        ratio = chars / openai_tokens
        print(f"   {label} text:")
        print(f"      Characters: {chars:,}")
        print(f"      Tokens: {openai_tokens:,}")
        print(f"      Char/Token ratio: {ratio:.2f}")

    print("\n1.3 Page Estimation:")
    pages = [1, 10, 100, 500]
    for page_count in pages:
        estimated = estimate_page_tokens(page_count)
        print(f"   {page_count:,} pages ≈ {estimated:,} tokens")

    print("\n1.4 Message Format Overhead:")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a programming language."},
    ]
    message_tokens = counter.count_messages_tokens(messages, 'gpt-5.4-mini', 'openai')
    raw_tokens = sum(counter.count_openai_tokens(m['content'], 'gpt-5.4-mini') for m in messages)
    overhead = message_tokens - raw_tokens
    print(f"   Raw content tokens: {raw_tokens}")
    print(f"   Message format tokens: {message_tokens}")
    print(f"   Overhead: {overhead} tokens ({(overhead/message_tokens)*100:.1f}%)")


def demo_context_management():
    """Demo 2: Context Management"""
    print_section("DEMO 2: Context Management with Sliding Windows")

    # Create a long conversation history
    conversation = []
    for i in range(15):
        conversation.append({
            "role": "user",
            "content": f"Question {i+1}: Can you explain topic {i+1}?"
        })
        conversation.append({
            "role": "assistant",
            "content": f"Answer {i+1}: Here's a detailed explanation of topic {i+1}. " * 30
        })

    manager = ContextManager(
        model="gpt-5.4-mini",
        provider="openai",
        context_limit=8192
    )

    print("2.1 Original Conversation:")
    total_tokens = manager.count_messages_tokens(conversation)
    print(f"   Messages: {len(conversation)}")
    print(f"   Total tokens: {total_tokens:,}")

    print("\n2.2 Truncation Strategies:")

    # Strategy 1: Simple sliding window
    max_tokens = 2000
    truncated_simple = manager.truncate_history_simple(conversation, max_tokens)
    print(f"   Simple Sliding Window (budget: {max_tokens:,} tokens):")
    print(f"      Messages kept: {len(truncated_simple)}")
    print(f"      Tokens: {manager.count_messages_tokens(truncated_simple):,}")

    # Strategy 2: Preserve pairs
    truncated_pairs = manager.truncate_history_preserve_pairs(conversation, max_tokens)
    print(f"\n   Preserve Message Pairs (budget: {max_tokens:,} tokens):")
    print(f"      Messages kept: {len(truncated_pairs)}")
    print(f"      Tokens: {manager.count_messages_tokens(truncated_pairs):,}")

    # Strategy 3: Selective retention
    truncated_selective = manager.truncate_history_selective(
        conversation,
        max_tokens,
        keep_first_n=2,
        keep_last_n=4
    )
    print(f"\n   Selective (first 2 + last 4) (budget: {max_tokens:,} tokens):")
    print(f"      Messages kept: {len(truncated_selective)}")
    print(f"      Tokens: {manager.count_messages_tokens(truncated_selective):,}")

    print("\n2.3 Complete Request Building:")
    system_prompt = "You are a knowledgeable AI assistant specializing in software development."
    current_message = "How do I optimize my code for performance?"
    retrieval_docs = [
        "Performance optimization requires profiling and benchmarking...",
        "Common bottlenecks include database queries and API calls...",
        "Use caching strategies to reduce redundant computations..."
    ]

    request = manager.build_request(
        system_prompt=system_prompt,
        conversation_history=conversation,
        current_message=current_message,
        retrieval_docs=retrieval_docs,
        response_budget=1500
    )

    print(f"   System tokens: {request['metadata']['system_tokens']:,}")
    print(f"   History tokens: {request['metadata']['history_tokens']:,}")
    print(f"   Retrieval tokens: {request['metadata']['retrieval_tokens']:,}")
    print(f"   Total input tokens: {request['metadata']['total_input_tokens']:,}")
    print(f"   Context utilization: {request['metadata']['utilization_pct']:.1f}%")
    print(f"   Messages kept: {request['metadata']['messages_kept']}/{len(conversation)}")


def demo_token_budgeting():
    """Demo 3: Dynamic Token Budget Planning"""
    print_section("DEMO 3: Dynamic Token Budget Planning")

    planner = TokenBudgetPlanner(
        context_limit=16384,  # Deliberately constrained application budget
        model="gpt-5.4-mini",
        provider="openai"
    )

    # Fixed components
    system_prompt_tokens = 500
    tools_tokens = 2000

    # Test different query complexities
    queries = {
        "simple": "What's your refund policy?",
        "medium": "How does your warranty compare to competitors?",
        "complex": "Analyze all customer feedback and identify top improvement areas"
    }

    print("3.1 Budget Planning by Query Complexity:\n")

    for complexity_name, query in queries.items():
        print(f"   Query: {query}")
        print(f"   {'─' * 70}")

        budget = planner.plan_budget(
            query=query,
            system_prompt_tokens=system_prompt_tokens,
            tools_tokens=tools_tokens,
            available_retrieval_chunks=20,
            available_history_messages=30
        )

        complexity = planner.classify_query_complexity(query)
        print(f"   Detected Complexity: {complexity.value}")
        print(f"   Token Allocation:")
        print(f"      Retrieval: {budget.retrieval:,} tokens")
        print(f"      History:   {budget.history:,} tokens")
        print(f"      Response:  {budget.response:,} tokens")
        print(f"      Total:     {budget.total_used:,}/{budget.total_available:,} ({budget.utilization_pct:.1f}%)")
        print()

    print("\n3.2 Usage Statistics:")
    stats = planner.get_usage_statistics()
    print(f"   Total requests analyzed: {stats['total_requests']}")
    print(f"   Average utilization: {stats['avg_utilization_pct']:.1f}%")
    print(f"   Complexity breakdown:")
    for complexity, count in stats['complexity_breakdown'].items():
        pct = (count / stats['total_requests']) * 100
        print(f"      {complexity}: {count} ({pct:.0f}%)")

    print("\n3.3 Optimization Suggestions:")
    suggestions = planner.suggest_optimizations()
    for suggestion in suggestions:
        print(f"   {suggestion}")


def demo_retrieval_truncation():
    """Demo 4: Smart Retrieval Truncation"""
    print_section("DEMO 4: Smart Retrieval Truncation Strategies")

    # Sample documents
    docs = [
        {"content": "Python is widely used for AI and machine learning. " * 25, "score": 0.95, "source": "python.md"},
        {"content": "JavaScript powers modern web applications. " * 20, "score": 0.85, "source": "javascript.md"},
        {"content": "TypeScript adds type safety to JavaScript. " * 22, "score": 0.80, "source": "typescript.md"},
        {"content": "Java is used in enterprise applications. " * 30, "score": 0.70, "source": "java.md"},
        {"content": "Go is excellent for concurrent systems. " * 15, "score": 0.65, "source": "go.md"},
        {"content": "Rust provides memory safety without garbage collection. " * 18, "score": 0.60, "source": "rust.md"},
    ]

    truncator = RetrievalTruncator(model="gpt-5.4-mini", provider="openai")
    results = truncator.prepare_retrieval_results(docs)

    total_tokens = sum(r.tokens for r in results)
    max_tokens = 1500

    print("4.1 Original Documents:")
    print(f"   Total documents: {len(results)}")
    print(f"   Total tokens: {total_tokens:,}")
    print(f"   Target budget: {max_tokens:,} tokens\n")

    # Compare strategies
    strategies = {
        "Top-N": truncator.truncate_top_n,
        "Proportional": truncator.truncate_proportional,
        "Position-Aware": truncator.truncate_position_aware,
        "Diverse": truncator.truncate_diverse,
    }

    print("4.2 Strategy Comparison:\n")
    print(f"   {'Strategy':<20} {'Docs':<8} {'Tokens':<10} {'Utilization':<12}")
    print(f"   {'-' * 60}")

    strategy_results = {}
    for strategy_name, strategy_func in strategies.items():
        selected, tokens_used = strategy_func(results, max_tokens)
        utilization = (tokens_used / max_tokens) * 100
        strategy_results[strategy_name] = (selected, tokens_used)
        print(f"   {strategy_name:<20} {len(selected):<8} {tokens_used:<10,} {utilization:.1f}%")

    # Show detailed breakdown for Position-Aware
    print("\n4.3 Position-Aware Strategy Detail:")
    pos_results, pos_tokens = strategy_results["Position-Aware"]
    print("   Document positioning (to avoid 'lost in the middle'):")
    for i, result in enumerate(pos_results, 1):
        position = "START (medium relevance)" if i <= len(pos_results)//2 else "END (high relevance)"
        print(f"      {i}. {result.source:<20} score: {result.score:.2f}  →  {position}")

    print("\n4.4 Formatted Context (first 400 chars):")
    formatted = truncator.format_for_context(
        pos_results[:3],  # Show first 3 for demo
        include_scores=True,
        include_sources=True
    )
    print("   " + formatted[:400].replace("\n", "\n   ") + "...\n")


def demo_production_scenario():
    """Demo 5: Complete Production Scenario"""
    print_section("DEMO 5: Complete Production Scenario")

    print("Scenario: Customer support chatbot with RAG")
    print("-" * 80)

    # Initialize components
    counter = TokenCounter()
    manager = ContextManager(model="gpt-5.4-mini", provider="openai", context_limit=400_000)
    planner = TokenBudgetPlanner(context_limit=400_000, model="gpt-5.4-mini")
    truncator = RetrievalTruncator(model="gpt-5.4-mini")

    # Simulate components
    system_prompt = """You are a helpful customer support agent for TechCorp.
    Use the retrieved documentation to answer questions accurately.
    Always be polite and professional."""

    conversation_history = []
    for i in range(8):
        conversation_history.append({"role": "user", "content": f"User question {i+1}"})
        conversation_history.append({"role": "assistant", "content": f"Detailed answer {i+1}. " * 50})

    user_query = "How do I upgrade my subscription plan and what are the pricing differences?"

    # Retrieved documents (simulated)
    retrieved_docs = [
        {"content": "Subscription plans include Basic, Pro, and Enterprise. " * 30, "score": 0.92, "source": "plans.md"},
        {"content": "Pricing: Basic $10/mo, Pro $50/mo, Enterprise custom. " * 25, "score": 0.90, "source": "pricing.md"},
        {"content": "To upgrade, go to Settings > Billing > Change Plan. " * 20, "score": 0.88, "source": "upgrade.md"},
        {"content": "Payment methods accepted: credit card, PayPal, wire. " * 18, "score": 0.75, "source": "payment.md"},
    ]

    print("\n5.1 Input Analysis:")
    system_tokens = counter.count_openai_tokens(system_prompt, "gpt-5.4-mini")
    history_tokens = manager.count_messages_tokens(conversation_history)
    query_tokens = counter.count_openai_tokens(user_query, "gpt-5.4-mini")

    retrieval_results = truncator.prepare_retrieval_results(retrieved_docs)
    total_retrieval_tokens = sum(r.tokens for r in retrieval_results)

    print(f"   System prompt: {system_tokens:,} tokens")
    print(f"   Conversation history: {history_tokens:,} tokens ({len(conversation_history)} messages)")
    print(f"   User query: {query_tokens:,} tokens")
    print(f"   Retrieved docs: {total_retrieval_tokens:,} tokens ({len(retrieved_docs)} documents)")

    print("\n5.2 Budget Planning:")
    budget = planner.plan_budget(
        query=user_query,
        system_prompt_tokens=system_tokens,
        tools_tokens=0,  # No tools in this scenario
        available_retrieval_chunks=len(retrieved_docs),
        available_history_messages=len(conversation_history)
    )

    complexity = planner.classify_query_complexity(user_query)
    print(f"   Query complexity: {complexity.value}")
    print(f"   Allocated budgets:")
    print(f"      Retrieval: {budget.retrieval:,} tokens")
    print(f"      History: {budget.history:,} tokens")
    print(f"      Response: {budget.response:,} tokens")

    print("\n5.3 Context Assembly:")

    # Truncate retrieval
    truncated_retrieval, retrieval_tokens_used = truncator.truncate_position_aware(
        retrieval_results,
        budget.retrieval
    )
    print(f"   Retrieval: {len(truncated_retrieval)}/{len(retrieved_docs)} docs, {retrieval_tokens_used:,} tokens")

    # Truncate history
    truncated_history = manager.truncate_history_preserve_pairs(
        conversation_history,
        budget.history
    )
    print(f"   History: {len(truncated_history)}/{len(conversation_history)} messages")

    # Build final request
    retrieval_content = [r.content for r in truncated_retrieval]
    request = manager.build_request(
        system_prompt=system_prompt,
        conversation_history=truncated_history,
        current_message=user_query,
        retrieval_docs=retrieval_content,
        response_budget=budget.response
    )

    print("\n5.4 Final Request Summary:")
    print(f"   Total input tokens: {request['metadata']['total_input_tokens']:,}")
    print(f"   Context limit: {request['metadata']['context_limit']:,}")
    print(f"   Utilization: {request['metadata']['utilization_pct']:.1f}%")
    input_price_per_token = 0.75 / 1_000_000
    output_price_per_token = 4.50 / 1_000_000
    print(f"   Cost estimate (GPT-5.4 mini, prices verified 2026-06-18): "
          f"${request['metadata']['total_input_tokens'] * input_price_per_token:.4f} input")
    print(f"                                 + ${budget.response * output_price_per_token:.4f} output (maximum)")

    total_cost = (
        request['metadata']['total_input_tokens'] * input_price_per_token
        + budget.response * output_price_per_token
    )
    print(f"                                 = ${total_cost:.4f} total")

    print("\n5.5 Efficiency Metrics:")
    original_tokens = system_tokens + history_tokens + query_tokens + total_retrieval_tokens
    final_tokens = request['metadata']['total_input_tokens']
    savings_pct = ((original_tokens - final_tokens) / original_tokens) * 100
    print(f"   Original size: {original_tokens:,} tokens")
    print(f"   Optimized size: {final_tokens:,} tokens")
    print(f"   Reduction: {original_tokens - final_tokens:,} tokens ({savings_pct:.1f}%)")


def main():
    """Run all demos."""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  Context Windows & Token Budgets - Complete Demonstration".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)

    demo_token_counting()
    demo_context_management()
    demo_token_budgeting()
    demo_retrieval_truncation()
    demo_production_scenario()

    print("\n" + "=" * 80)
    print("  Demo Complete!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  1. Use provider counting APIs for hard production limits")
    print("  2. Budget your context carefully across components")
    print("  3. Use smart truncation strategies to maximize quality")
    print("  4. Position-aware placement avoids 'lost in the middle'")
    print("  5. Monitor usage patterns to optimize costs and quality")
    print("\nNext Steps:")
    print("  • Experiment with different truncation strategies")
    print("  • Profile your actual token usage in production")
    print("  • Implement monitoring and alerting")
    print("  • Test different model sizes to find the optimal fit")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError running demo: {e}")
        print("Make sure you have installed the requirements:")
        print("  pip install -r requirements.txt")
