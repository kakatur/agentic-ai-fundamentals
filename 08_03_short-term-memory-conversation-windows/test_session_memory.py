import pytest

from session_memory import Message, add_message, build_conversation_window, render_window, trim_to_recent_pairs


def test_add_message_rejects_unknown_role():
    with pytest.raises(ValueError):
        add_message((), "tool?", "bad")


def test_trim_preserves_recent_user_assistant_pairs():
    history = (
        Message("user", "one"),
        Message("assistant", "answer one"),
        Message("user", "two"),
        Message("assistant", "answer two"),
        Message("user", "three"),
    )
    kept = trim_to_recent_pairs(history, max_pairs=2)
    assert kept == history[2:]


def test_window_keeps_pinned_facts_outside_trimmed_history():
    history = (
        Message("user", "old preference"),
        Message("assistant", "saved"),
        Message("user", "new question"),
    )
    window = build_conversation_window(history, ("prefers concise answers",), max_pairs=1)
    rendered = render_window(window)
    assert "prefers concise answers" in rendered
    assert "old preference" not in rendered
    assert "new question" in rendered
