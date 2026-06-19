import pytest

from context_manager import ContextManager
from retrieval_truncation import RetrievalResult, RetrievalTruncator
from token_budget_planner import QueryComplexity, TokenBudgetPlanner
from token_counter import TokenCounter


def test_anthropic_counting_has_offline_fallback():
    counter = TokenCounter()
    assert counter.count_anthropic_tokens("Hello, Claude") > 0


def test_build_request_reserves_current_message_and_response():
    manager = ContextManager(
        model="gpt-5.4-mini",
        provider="openai",
        context_limit=256,
    )
    result = manager.build_request(
        system_prompt="Be concise.",
        conversation_history=[
            {"role": "user", "content": "old question " * 100},
            {"role": "assistant", "content": "old answer " * 100},
        ],
        current_message="current question",
        response_budget=64,
    )

    assert result["messages"][-1]["content"] == "current question"
    assert result["metadata"]["reserved_total_tokens"] <= 256


def test_build_request_rejects_fixed_components_that_cannot_fit():
    manager = ContextManager(
        model="gpt-5.4-mini",
        provider="openai",
        context_limit=32,
    )

    with pytest.raises(ValueError):
        manager.build_request(
            system_prompt="system " * 50,
            conversation_history=[],
            current_message="question",
            response_budget=16,
        )


def test_top_n_skips_oversized_document_and_keeps_smaller_one():
    truncator = RetrievalTruncator()
    results = [
        RetrievalResult("large", 1.0, "large.md", 200),
        RetrievalResult("small", 0.9, "small.md", 20),
    ]

    selected, total = truncator.truncate_top_n(results, max_tokens=50)

    assert [item.source for item in selected] == ["small.md"]
    assert total == 20


def test_openai_truncation_obeys_token_limit():
    truncator = RetrievalTruncator(model="gpt-5.4-mini")
    text = "context engineering " * 100
    truncated = truncator._truncate_text_to_tokens(text, max_tokens=25)

    assert truncator.count_tokens(truncated) <= 25


def test_position_aware_keeps_all_documents_when_they_fit():
    truncator = RetrievalTruncator()
    results = [
        RetrievalResult("high", 0.9, "high.md", 20),
        RetrievalResult("low", 0.5, "low.md", 20),
        RetrievalResult("medium", 0.7, "medium.md", 20),
    ]

    selected, total = truncator.truncate_position_aware(results, max_tokens=100)

    assert [item.source for item in selected] == [
        "low.md",
        "medium.md",
        "high.md",
    ]
    assert total == 60


def test_budget_planner_caps_allocations_to_available_data():
    planner = TokenBudgetPlanner(context_limit=400_000)
    budget = planner.plan_budget(
        query="How does this compare?",
        system_prompt_tokens=100,
        tools_tokens=0,
        available_retrieval_chunks=2,
        available_history_messages=3,
    )

    assert planner.classify_query_complexity("How does this compare?") == QueryComplexity.MEDIUM
    assert budget.retrieval == 1_000
    assert budget.history == 300
    assert budget.utilization_pct < 5
