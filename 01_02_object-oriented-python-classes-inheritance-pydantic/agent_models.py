from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


ALLOWED_PRIORITIES = {"low", "normal", "high"}


@dataclass(frozen=True)
class AgentRequest:
    user_id: str
    message: str
    priority: str = "normal"
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.user_id.strip():
            raise ValueError("user_id is required")
        if not self.message.strip():
            raise ValueError("message is required")
        if self.priority not in ALLOWED_PRIORITIES:
            raise ValueError(f"priority must be one of {sorted(ALLOWED_PRIORITIES)}")


@dataclass(frozen=True)
class AgentResponse:
    agent_name: str
    answer: str
    blocked: bool = False
    reason: str | None = None


class Agent(Protocol):
    name: str

    def handle(self, request: AgentRequest) -> AgentResponse:
        ...


class BaseAgent:
    def __init__(self, name: str) -> None:
        if not name:
            raise ValueError("agent name is required")
        self.name = name

    def format_answer(self, request: AgentRequest) -> str:
        return f"{request.priority}: {request.message}"


class EchoAgent(BaseAgent):
    def handle(self, request: AgentRequest) -> AgentResponse:
        return AgentResponse(agent_name=self.name, answer=self.format_answer(request))


class ModeratedAgent(EchoAgent):
    blocked_terms = {"password", "secret"}

    def handle(self, request: AgentRequest) -> AgentResponse:
        lowered = request.message.lower()
        if any(term in lowered for term in self.blocked_terms):
            return AgentResponse(
                agent_name=self.name,
                answer="Request blocked",
                blocked=True,
                reason="message contained sensitive term",
            )
        return super().handle(request)


def request_schema() -> dict[str, object]:
    return {
        "type": "object",
        "required": ["user_id", "message"],
        "properties": {
            "user_id": {"type": "string"},
            "message": {"type": "string"},
            "priority": {"type": "string", "enum": sorted(ALLOWED_PRIORITIES)},
        },
    }
