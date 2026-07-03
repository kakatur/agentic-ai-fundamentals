import pytest

from conversation_store import ConversationStore, Message


def test_store_round_trips_messages_in_order():
    store = ConversationStore(":memory:")
    store.add_message("c1", "user", "hello")
    store.add_message("c1", "assistant", "hi")
    assert store.list_messages("c1") == [
        Message("c1", "user", "hello"),
        Message("c1", "assistant", "hi"),
    ]


def test_parameterized_query_treats_injection_as_text():
    store = ConversationStore(":memory:")
    store.add_message("safe", "user", "hello")
    assert store.list_messages("safe' OR '1'='1") == []


def test_invalid_role_fails_before_insert():
    store = ConversationStore(":memory:")
    with pytest.raises(ValueError):
        store.add_message("c1", "admin", "hello")


def test_search_content_uses_parameter_binding():
    store = ConversationStore(":memory:")
    store.add_message("c1", "user", "find the invoice")
    assert store.search_content("invoice")[0].conversation_id == "c1"
