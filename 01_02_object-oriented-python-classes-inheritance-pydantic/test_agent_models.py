import pytest

from agent_models import AgentRequest, EchoAgent, ModeratedAgent, request_schema


def test_agent_request_validates_required_fields():
    with pytest.raises(ValueError):
        AgentRequest(user_id="", message="hello")
    with pytest.raises(ValueError):
        AgentRequest(user_id="u-1", message="hello", priority="urgent")


def test_echo_agent_uses_base_formatting():
    response = EchoAgent("echo").handle(AgentRequest(user_id="u-1", message="hello", priority="high"))
    assert response.answer == "high: hello"
    assert response.blocked is False


def test_moderated_agent_inherits_and_overrides_behavior():
    response = ModeratedAgent("guarded").handle(AgentRequest(user_id="u-1", message="my password is here"))
    assert response.blocked is True
    assert response.reason == "message contained sensitive term"


def test_schema_documents_validation_boundary():
    schema = request_schema()
    assert schema["properties"]["priority"]["enum"] == ["high", "low", "normal"]
