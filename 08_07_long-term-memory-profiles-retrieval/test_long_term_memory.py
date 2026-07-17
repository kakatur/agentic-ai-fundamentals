import pytest

from long_term_memory import LongTermMemory


def test_remember_validates_confidence():
    memory = LongTermMemory()
    with pytest.raises(ValueError):
        memory.remember("u1", "tone", "short", "test", confidence=2)


def test_profile_uses_latest_matching_key():
    memory = LongTermMemory()
    memory.remember("u1", "tone", "formal", "old")
    memory.remember("u1", "tone", "concise", "new")
    assert memory.profile("u1")["tone"] == "concise"


def test_profile_filters_low_confidence_records():
    memory = LongTermMemory()
    memory.remember("u1", "timezone", "Pacific", "guess", confidence=0.4)
    assert memory.profile("u1", min_confidence=0.8) == {}


def test_retrieve_is_scoped_to_user():
    memory = LongTermMemory()
    memory.remember("u1", "project", "billing migration", "ticket")
    memory.remember("u2", "project", "billing migration", "ticket")
    records = memory.retrieve("u1", "billing")
    assert len(records) == 1
    assert records[0].user_id == "u1"
