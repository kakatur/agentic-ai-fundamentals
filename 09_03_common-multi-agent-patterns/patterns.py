"""Deterministic examples of common multi-agent coordination patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Route(StrEnum):
    BILLING = "billing"
    SECURITY = "security"
    TECHNICAL = "technical"
    SYNTHESIS = "synthesis"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True)
class Task:
    customer_id: str
    request: str
    priority: int = 1


@dataclass(frozen=True)
class AgentReply:
    agent: str
    route: Route
    answer: str
    confidence: float
    facts: tuple[str, ...] = ()


@dataclass(frozen=True)
class Handoff:
    sender: str
    receiver: str
    reason: str
    payload: dict[str, str]


@dataclass(frozen=True)
class WorkflowResult:
    route: Route
    answer: str
    confidence: float
    replies: tuple[AgentReply, ...]
    handoffs: tuple[Handoff, ...] = field(default_factory=tuple)
    verified: bool = False


class SpecialistAgent:
    """A focused agent with a narrow route and keyword-based confidence."""

    def __init__(
        self,
        *,
        name: str,
        route: Route,
        keywords: tuple[str, ...],
        response_template: str,
    ) -> None:
        self.name = name
        self.route = route
        self.keywords = keywords
        self.response_template = response_template

    def handle(self, task: Task) -> AgentReply:
        lowered = task.request.lower()
        matches = tuple(word for word in self.keywords if word in lowered)
        confidence = min(0.95, 0.45 + 0.2 * len(matches))
        if task.priority >= 4:
            confidence -= 0.1

        return AgentReply(
            agent=self.name,
            route=self.route,
            answer=self.response_template.format(customer_id=task.customer_id),
            confidence=max(0.0, round(confidence, 2)),
            facts=matches,
        )


class Coordinator:
    """Routes work to specialists and owns the final workflow decision."""

    def __init__(self, specialists: tuple[SpecialistAgent, ...]) -> None:
        self.specialists = specialists

    def route(self, task: Task) -> tuple[SpecialistAgent, ...]:
        replies = [agent.handle(task) for agent in self.specialists]
        relevant = [
            agent
            for agent, reply in zip(self.specialists, replies, strict=True)
            if reply.facts
        ]
        if relevant:
            return tuple(relevant)
        fallback, _reply = max(
            zip(self.specialists, replies, strict=True),
            key=lambda item: item[1].confidence,
        )
        return (fallback,)

    def run_router_pattern(self, task: Task) -> WorkflowResult:
        agent = self.route(task)[0]
        reply = agent.handle(task)
        handoff = Handoff(
            sender="coordinator",
            receiver=agent.name,
            reason=f"request matched {agent.route.value} scope",
            payload={"customer_id": task.customer_id, "request": task.request},
        )

        if reply.confidence < 0.6 or task.priority >= 5:
            escalation = Handoff(
                sender=agent.name,
                receiver="human_review",
                reason="low confidence or critical priority",
                payload={"route": agent.route.value, "confidence": str(reply.confidence)},
            )
            return WorkflowResult(
                route=Route.HUMAN_REVIEW,
                answer="Escalated for human review.",
                confidence=reply.confidence,
                replies=(reply,),
                handoffs=(handoff, escalation),
            )

        return WorkflowResult(
            route=agent.route,
            answer=reply.answer,
            confidence=reply.confidence,
            replies=(reply,),
            handoffs=(handoff,),
        )

    def run_parallel_pattern(self, task: Task) -> WorkflowResult:
        selected = self.route(task)
        replies = tuple(agent.handle(task) for agent in selected)
        handoffs = tuple(
            Handoff(
                sender="coordinator",
                receiver=agent.name,
                reason="parallel specialist review",
                payload={"customer_id": task.customer_id, "request": task.request},
            )
            for agent in selected
        )
        confidence = round(sum(reply.confidence for reply in replies) / len(replies), 2)
        answer = " | ".join(reply.answer for reply in replies)
        route = replies[0].route if len(replies) == 1 else Route.SYNTHESIS
        return WorkflowResult(
            route=route,
            answer=answer,
            confidence=confidence,
            replies=replies,
            handoffs=handoffs,
        )


class VerifierAgent:
    """Checks whether a produced answer is supported by the specialist facts."""

    def verify(self, task: Task, reply: AgentReply) -> bool:
        if not reply.facts:
            return False
        lowered_answer = reply.answer.lower()
        return reply.route.value in lowered_answer or task.customer_id in reply.answer


def run_producer_verifier_pattern(
    task: Task,
    producer: SpecialistAgent,
    verifier: VerifierAgent,
) -> WorkflowResult:
    reply = producer.handle(task)
    verified = verifier.verify(task, reply)
    verification_handoff = Handoff(
        sender=producer.name,
        receiver="verifier",
        reason="independent answer check",
        payload={"answer": reply.answer, "facts": ", ".join(reply.facts)},
    )

    if not verified:
        escalation = Handoff(
            sender="verifier",
            receiver="human_review",
            reason="answer was not supported by producer facts",
            payload={"producer": producer.name},
        )
        return WorkflowResult(
            route=Route.HUMAN_REVIEW,
            answer="Verifier rejected the answer.",
            confidence=reply.confidence,
            replies=(reply,),
            handoffs=(verification_handoff, escalation),
            verified=False,
        )

    return WorkflowResult(
        route=reply.route,
        answer=reply.answer,
        confidence=reply.confidence,
        replies=(reply,),
        handoffs=(verification_handoff,),
        verified=True,
    )


def default_specialists() -> tuple[SpecialistAgent, ...]:
    return (
        SpecialistAgent(
            name="billing_agent",
            route=Route.BILLING,
            keywords=("refund", "invoice", "charge", "payment"),
            response_template="Billing answer for {customer_id}: review invoice and payment history.",
        ),
        SpecialistAgent(
            name="security_agent",
            route=Route.SECURITY,
            keywords=("login", "password", "security", "access"),
            response_template="Security answer for {customer_id}: verify identity and recent access.",
        ),
        SpecialistAgent(
            name="technical_agent",
            route=Route.TECHNICAL,
            keywords=("error", "api", "timeout", "integration"),
            response_template="Technical answer for {customer_id}: inspect integration logs.",
        ),
    )


def default_coordinator() -> Coordinator:
    return Coordinator(default_specialists())
