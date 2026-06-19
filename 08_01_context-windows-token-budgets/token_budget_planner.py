"""
Token Budget Planner - Dynamic token budget allocation

This module implements intelligent token budget planning that adapts
based on query complexity, historical usage, and available capacity.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from token_counter import TokenCounter


class QueryComplexity(Enum):
    """Query complexity levels for adaptive budgeting."""
    SIMPLE = "simple"       # "What's your return policy?"
    MEDIUM = "medium"       # "How does your warranty compare to competitors?"
    COMPLEX = "complex"     # "Analyze all product reviews and identify trends"


@dataclass
class TokenBudget:
    """Token budget allocation breakdown."""
    system_prompt: int
    tools: int
    retrieval: int
    history: int
    response: int
    total_used: int
    total_available: int
    utilization_pct: float


class TokenBudgetPlanner:
    """
    Plans and allocates token budgets dynamically based on query needs.

    Key features:
    - Query complexity classification
    - Dynamic budget allocation
    - Historical usage tracking
    - Adaptive optimization
    """

    def __init__(
        self,
        context_limit: int,
        model: str = "gpt-5.4-mini",
        provider: str = "openai"
    ):
        self.context_limit = context_limit
        self.model = model
        self.provider = provider
        self.counter = TokenCounter()
        self.usage_history = []

    def classify_query_complexity(self, query: str) -> QueryComplexity:
        """
        Classify query complexity to guide budget allocation.

        In production, you might:
        1. Use an LLM to classify
        2. Train a small classifier model
        3. Use heuristics (query length, keywords, question marks)

        Here we use simple heuristics for demonstration.

        Args:
            query: User query

        Returns:
            QueryComplexity enum
        """
        query_lower = query.lower()

        # Heuristic indicators
        complex_keywords = [
            "analyze", "summarize", "explain in detail",
            "comprehensive", "all", "every", "trends", "patterns"
        ]
        medium_keywords = [
            "how", "why", "difference", "versus", "vs",
            "which", "best", "recommend"
        ]

        # Count indicators
        complex_score = sum(1 for kw in complex_keywords if kw in query_lower)
        medium_score = sum(1 for kw in medium_keywords if kw in query_lower)

        # Length heuristic
        word_count = len(query.split())

        if complex_score > 0 or word_count > 30:
            return QueryComplexity.COMPLEX
        elif medium_score > 0 or word_count > 15:
            return QueryComplexity.MEDIUM
        else:
            return QueryComplexity.SIMPLE

    def plan_budget(
        self,
        query: str,
        system_prompt_tokens: int,
        tools_tokens: int,
        available_retrieval_chunks: int = 10,
        available_history_messages: int = 20,
        complexity: Optional[QueryComplexity] = None
    ) -> TokenBudget:
        """
        Plan token budget allocation based on query complexity.

        Args:
            query: User query
            system_prompt_tokens: Tokens used by system prompt
            tools_tokens: Tokens used by tool definitions
            available_retrieval_chunks: Number of chunks available to retrieve
            available_history_messages: Number of history messages available
            complexity: Optional pre-classified complexity

        Returns:
            TokenBudget with allocation plan
        """
        # Classify query if not provided
        if complexity is None:
            complexity = self.classify_query_complexity(query)

        # Fixed allocations
        query_tokens = self._count_tokens(query)
        response_budget = self._estimate_response_size(complexity)

        # Calculate available tokens for dynamic allocation
        fixed_tokens = (
            system_prompt_tokens +
            tools_tokens +
            query_tokens +
            response_budget
        )

        available_for_allocation = self.context_limit - fixed_tokens

        # Add safety buffer (5%)
        safety_buffer = int(self.context_limit * 0.05)
        available_for_allocation -= safety_buffer

        if available_for_allocation < 0:
            # Not enough space even for fixed components!
            raise ValueError(
                f"Fixed components exceed context limit. "
                f"Used: {fixed_tokens}, Limit: {self.context_limit}"
            )

        # Allocate based on complexity
        allocation_strategy = self._get_allocation_strategy(complexity)

        target_retrieval_budget = int(
            available_for_allocation * allocation_strategy["retrieval_pct"]
        )
        target_history_budget = int(
            available_for_allocation * allocation_strategy["history_pct"]
        )

        # Cap allocations at the amount of data actually available.
        avg_chunk_tokens = 500  # Typical chunk size
        retrieval_budget = min(
            target_retrieval_budget,
            available_retrieval_chunks * avg_chunk_tokens,
        )
        retrieval_chunks_to_use = min(
            available_retrieval_chunks,
            retrieval_budget // avg_chunk_tokens
        )

        avg_message_tokens = 100  # Typical message size
        history_budget = min(
            target_history_budget,
            available_history_messages * avg_message_tokens,
        )
        history_messages_to_use = min(
            available_history_messages,
            history_budget // avg_message_tokens
        )

        total_used = (
            system_prompt_tokens +
            tools_tokens +
            query_tokens +
            retrieval_budget +
            history_budget +
            response_budget
        )

        utilization_pct = (total_used / self.context_limit) * 100

        budget = TokenBudget(
            system_prompt=system_prompt_tokens,
            tools=tools_tokens,
            retrieval=retrieval_budget,
            history=history_budget,
            response=response_budget,
            total_used=total_used,
            total_available=self.context_limit,
            utilization_pct=utilization_pct
        )

        # Track for historical optimization
        self.usage_history.append({
            "complexity": complexity,
            "budget": budget,
            "retrieval_chunks": retrieval_chunks_to_use,
            "history_messages": history_messages_to_use
        })

        return budget

    def _get_allocation_strategy(
        self,
        complexity: QueryComplexity
    ) -> Dict[str, float]:
        """
        Get allocation percentages based on complexity.

        Args:
            complexity: Query complexity level

        Returns:
            Dict with retrieval_pct and history_pct
        """
        strategies = {
            QueryComplexity.SIMPLE: {
                "retrieval_pct": 0.30,  # Simple queries need less retrieval
                "history_pct": 0.70,    # More history for conversational continuity
                "description": "Prioritize conversation history"
            },
            QueryComplexity.MEDIUM: {
                "retrieval_pct": 0.50,  # Balanced
                "history_pct": 0.50,
                "description": "Balanced allocation"
            },
            QueryComplexity.COMPLEX: {
                "retrieval_pct": 0.70,  # Complex queries need more information
                "history_pct": 0.30,    # Less history needed
                "description": "Prioritize retrieval for comprehensive answers"
            }
        }
        return strategies[complexity]

    def _estimate_response_size(
        self,
        complexity: QueryComplexity
    ) -> int:
        """
        Estimate expected response size based on complexity.

        Args:
            complexity: Query complexity

        Returns:
            Estimated token count for response
        """
        estimates = {
            QueryComplexity.SIMPLE: 500,    # Short answer
            QueryComplexity.MEDIUM: 1000,   # Moderate answer
            QueryComplexity.COMPLEX: 2000   # Detailed answer
        }
        return estimates[complexity]

    def _count_tokens(self, text: str) -> int:
        """Count tokens for text."""
        if self.provider == "openai":
            return self.counter.count_openai_tokens(text, self.model)
        else:
            return self.counter.count_anthropic_tokens(text, self.model)

    def get_usage_statistics(self) -> Dict[str, any]:
        """
        Analyze historical usage to optimize future allocations.

        Returns:
            Statistics about token usage patterns
        """
        if not self.usage_history:
            return {"message": "No usage history yet"}

        total_requests = len(self.usage_history)

        # Calculate averages
        avg_utilization = sum(
            entry["budget"].utilization_pct for entry in self.usage_history
        ) / total_requests

        avg_retrieval = sum(
            entry["budget"].retrieval for entry in self.usage_history
        ) / total_requests

        avg_history = sum(
            entry["budget"].history for entry in self.usage_history
        ) / total_requests

        # Find requests that hit limits
        high_utilization = sum(
            1 for entry in self.usage_history
            if entry["budget"].utilization_pct > 85
        )

        # Complexity breakdown
        complexity_counts = {
            QueryComplexity.SIMPLE: 0,
            QueryComplexity.MEDIUM: 0,
            QueryComplexity.COMPLEX: 0
        }
        for entry in self.usage_history:
            complexity_counts[entry["complexity"]] += 1

        return {
            "total_requests": total_requests,
            "avg_utilization_pct": round(avg_utilization, 2),
            "avg_retrieval_tokens": round(avg_retrieval, 0),
            "avg_history_tokens": round(avg_history, 0),
            "high_utilization_count": high_utilization,
            "high_utilization_pct": round((high_utilization / total_requests) * 100, 2),
            "complexity_breakdown": {
                k.value: v for k, v in complexity_counts.items()
            }
        }

    def suggest_optimizations(self) -> List[str]:
        """
        Suggest optimizations based on usage patterns.

        Returns:
            List of optimization suggestions
        """
        stats = self.get_usage_statistics()

        if stats.get("message"):
            return ["Collect more usage data before optimizing"]

        suggestions = []

        # Check if consistently low utilization
        if stats["avg_utilization_pct"] < 40:
            suggestions.append(
                f"⚠️  Average utilization is only {stats['avg_utilization_pct']}%. "
                f"Consider using a model with smaller context (lower cost)."
            )

        # Check if frequently hitting limits
        if stats["high_utilization_pct"] > 20:
            suggestions.append(
                f"⚠️  {stats['high_utilization_pct']}% of requests use >85% of context. "
                f"Consider: (1) Using a larger context model, "
                f"(2) Implementing compression, or (3) Reducing retrieval."
            )

        # Check complexity distribution
        complexity = stats["complexity_breakdown"]
        if complexity.get("complex", 0) > complexity.get("simple", 0):
            suggestions.append(
                "💡 Most queries are complex. Consider implementing "
                "query decomposition or multi-stage retrieval."
            )

        if not suggestions:
            suggestions.append("✅ Current allocation strategy looks good!")

        return suggestions


# Example usage
if __name__ == "__main__":
    print("Token Budget Planner Demo")
    print("=" * 60)

    # Initialize planner
    planner = TokenBudgetPlanner(
        context_limit=16384,  # Deliberately constrained application budget
        model="gpt-5.4-mini",
        provider="openai"
    )

    # Fixed components
    system_prompt_tokens = 500
    tools_tokens = 2000

    # Test queries with different complexities
    test_queries = [
        "What's your return policy?",  # Simple
        "How does your warranty compare to the industry standard?",  # Medium
        "Analyze all customer reviews from the past year and identify the top 5 trends",  # Complex
    ]

    print("\nBudget Planning for Different Query Complexities:\n")

    for query in test_queries:
        print(f"Query: {query}")
        print("-" * 60)

        # Plan budget
        budget = planner.plan_budget(
            query=query,
            system_prompt_tokens=system_prompt_tokens,
            tools_tokens=tools_tokens,
            available_retrieval_chunks=20,
            available_history_messages=30
        )

        # Display results
        complexity = planner.classify_query_complexity(query)
        print(f"Complexity: {complexity.value}")
        print(f"\nToken Allocation:")
        print(f"  System Prompt: {budget.system_prompt:,} tokens")
        print(f"  Tools:         {budget.tools:,} tokens")
        print(f"  Retrieval:     {budget.retrieval:,} tokens")
        print(f"  History:       {budget.history:,} tokens")
        print(f"  Response:      {budget.response:,} tokens")
        print(f"  {'─' * 40}")
        print(f"  Total Used:    {budget.total_used:,} tokens")
        print(f"  Total Limit:   {budget.total_available:,} tokens")
        print(f"  Utilization:   {budget.utilization_pct:.1f}%")
        print("\n" + "=" * 60 + "\n")

    # Show usage statistics
    print("\nUsage Statistics:")
    print("=" * 60)
    stats = planner.get_usage_statistics()
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Average Utilization: {stats['avg_utilization_pct']}%")
    print(f"Average Retrieval: {stats['avg_retrieval_tokens']:,.0f} tokens")
    print(f"Average History: {stats['avg_history_tokens']:,.0f} tokens")
    print(f"\nComplexity Breakdown:")
    for complexity, count in stats['complexity_breakdown'].items():
        pct = (count / stats['total_requests']) * 100
        print(f"  {complexity}: {count} ({pct:.0f}%)")

    # Show optimization suggestions
    print("\n" + "=" * 60)
    print("Optimization Suggestions:")
    print("=" * 60)
    suggestions = planner.suggest_optimizations()
    for suggestion in suggestions:
        print(f"  {suggestion}")

    # Demonstrate model comparison
    print("\n" + "=" * 60)
    print("Model Context Comparison:")
    print("=" * 60)

    models = [
        ("Small application budget", 16_384),
        ("Medium application budget", 128_000),
        ("GPT-5.4 mini", 400_000),
        ("GPT-5.5", 1_050_000),
    ]

    complex_query = "Analyze all customer reviews and provide detailed insights"

    for model_name, context_limit in models:
        planner_temp = TokenBudgetPlanner(context_limit=context_limit)
        budget = planner_temp.plan_budget(
            query=complex_query,
            system_prompt_tokens=500,
            tools_tokens=2000,
            complexity=QueryComplexity.COMPLEX
        )
        print(f"\n{model_name} ({context_limit:,} tokens):")
        print(f"  Retrieval Budget: {budget.retrieval:,} tokens")
        print(f"  History Budget: {budget.history:,} tokens")
        print(f"  Utilization: {budget.utilization_pct:.1f}%")
