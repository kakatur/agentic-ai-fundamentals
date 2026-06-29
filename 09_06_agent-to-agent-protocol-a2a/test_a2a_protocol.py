import pytest

from a2a_protocol import A2AClient, TaskState, sample_registry


def test_registry_finds_agent_by_skill_tag():
    card = sample_registry().find("refund")
    assert card.name == "billing-agent"


def test_client_creates_and_completes_task():
    client = A2AClient(sample_registry())
    task = client.send_task("t1", "summarize", "Summarize this report")
    assert task.agent == "research-agent"
    assert task.state == TaskState.SUBMITTED
    done = client.complete_task("t1", "summary", "Short summary")
    assert done.state == TaskState.COMPLETED
    assert done.artifacts[0].name == "summary"


def test_unsupported_capability_fails_closed():
    with pytest.raises(LookupError):
        sample_registry().find("payments", mode="image")
