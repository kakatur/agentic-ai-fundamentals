import pytest

from memory_privacy import PrivateMemory, PrivacyAwareMemoryStore


def test_store_requires_consent():
    store = PrivacyAwareMemoryStore()
    with pytest.raises(ValueError):
        store.remember(PrivateMemory("m1", "u1", "preference", "short", consent=False))


def test_export_returns_only_requested_user_memories():
    store = PrivacyAwareMemoryStore()
    store.remember(PrivateMemory("m1", "u1", "preference", "short", consent=True))
    store.remember(PrivateMemory("m2", "u2", "preference", "formal", consent=True))
    exported = store.export_user("u1")
    assert len(exported) == 1
    assert exported[0].user_id == "u1"


def test_delete_user_removes_memories_and_suppresses_future_writes():
    store = PrivacyAwareMemoryStore()
    store.remember(PrivateMemory("m1", "u1", "preference", "short", consent=True))
    assert store.delete_user("u1") == 1
    assert store.export_user("u1") == ()
    with pytest.raises(ValueError):
        store.remember(PrivateMemory("m2", "u1", "preference", "short", consent=True))


def test_audit_log_records_memory_actions():
    store = PrivacyAwareMemoryStore()
    store.remember(PrivateMemory("m1", "u1", "preference", "short", consent=True))
    store.delete_user("u1")
    assert [event.action for event in store.audit_log("u1")] == ["remember", "delete"]
