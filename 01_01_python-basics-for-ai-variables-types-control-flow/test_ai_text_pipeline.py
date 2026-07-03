import pytest

from ai_text_pipeline import (
    build_request,
    classify_intent,
    classify_requests,
    estimate_tokens,
    normalize_text,
)


def test_normalize_text_collapses_whitespace():
    messy_text = "  summarize   this\nfile "

    assert normalize_text(messy_text) == "summarize this file"


def test_classify_intent_uses_control_flow():
    assert classify_intent("please summarize this") == "summarize"
    assert classify_intent("translate hello") == "translate"
    assert classify_intent("invoice total") == "extract"
    assert classify_intent("hello") == "chat"


def test_build_request_preserves_raw_and_normalized_values():
    request = build_request("  Extract invoice total ")

    assert request.raw_text.startswith("  ")
    assert request.normalized_text == "Extract invoice total"
    assert request.intent == "extract"
    assert request.valid is True


def test_classify_requests_filters_empty_items():
    results = classify_requests(["summarize", "   ", "hello"])
    assert [item.intent for item in results] == ["summarize", "chat"]


def test_normalize_text_rejects_non_string():
    with pytest.raises(TypeError):
        normalize_text(123)
