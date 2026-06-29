from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TaskState(StrEnum):
    SUBMITTED = "submitted"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class AgentSkill:
    id: str
    name: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class AgentCard:
    name: str
    url: str
    skills: tuple[AgentSkill, ...]
    input_modes: tuple[str, ...] = ("text",)
    output_modes: tuple[str, ...] = ("text",)

    def supports(self, tag: str, mode: str = "text") -> bool:
        return mode in self.input_modes and any(tag in skill.tags for skill in self.skills)


@dataclass(frozen=True)
class Message:
    role: str
    parts: tuple[str, ...]


@dataclass(frozen=True)
class Artifact:
    name: str
    parts: tuple[str, ...]


@dataclass(frozen=True)
class Task:
    id: str
    agent: str
    state: TaskState
    messages: tuple[Message, ...]
    artifacts: tuple[Artifact, ...] = ()


class AgentRegistry:
    def __init__(self, cards: tuple[AgentCard, ...]) -> None:
        self.cards = cards

    def find(self, tag: str, mode: str = "text") -> AgentCard:
        matches = [card for card in self.cards if card.supports(tag, mode)]
        if not matches:
            raise LookupError(f"no agent supports {tag!r} with {mode!r}")
        return sorted(matches, key=lambda card: card.name)[0]


class A2AClient:
    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry
        self.tasks: dict[str, Task] = {}

    def send_task(self, task_id: str, capability: str, text: str) -> Task:
        card = self.registry.find(capability)
        task = Task(
            id=task_id,
            agent=card.name,
            state=TaskState.SUBMITTED,
            messages=(Message("user", (text,)),),
        )
        self.tasks[task_id] = task
        return task

    def complete_task(self, task_id: str, artifact_name: str, text: str) -> Task:
        task = self.tasks[task_id]
        completed = Task(
            id=task.id,
            agent=task.agent,
            state=TaskState.COMPLETED,
            messages=task.messages,
            artifacts=(Artifact(artifact_name, (text,)),),
        )
        self.tasks[task_id] = completed
        return completed


def sample_registry() -> AgentRegistry:
    return AgentRegistry(
        (
            AgentCard(
                "billing-agent",
                "https://agents.example/billing",
                (AgentSkill("refunds", "Refund analysis", ("billing", "refund")),),
            ),
            AgentCard(
                "research-agent",
                "https://agents.example/research",
                (AgentSkill("summarize", "Research summary", ("research", "summarize")),),
            ),
        )
    )
