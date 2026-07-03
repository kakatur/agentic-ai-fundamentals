import asyncio

import pytest

from async_agent_calls import FakeModelClient, answer_many, answer_many_with_errors, answer_one, bounded_answer_many


def test_answer_one_returns_model_result():
    result = asyncio.run(answer_one(FakeModelClient(delay=0), "hello"))
    assert result.answer == "HELLO"


def test_answer_many_preserves_prompt_order():
    results = asyncio.run(answer_many(FakeModelClient(delay=0), ["a", "b", "c"]))
    assert [item.answer for item in results] == ["A", "B", "C"]


def test_timeout_becomes_exception_when_requested():
    results = asyncio.run(answer_many_with_errors(FakeModelClient(delay=0.05), ["slow"], timeout=0.001))
    assert isinstance(results[0], TimeoutError)


def test_bounded_answer_many_runs_all_prompts():
    results = asyncio.run(bounded_answer_many(FakeModelClient(delay=0), ["a", "b", "c"], limit=2))
    assert [item.prompt for item in results] == ["a", "b", "c"]


def test_answer_many_raises_timeout_without_return_exceptions():
    with pytest.raises(TimeoutError):
        asyncio.run(answer_many(FakeModelClient(delay=0.05), ["slow"], timeout=0.001))
