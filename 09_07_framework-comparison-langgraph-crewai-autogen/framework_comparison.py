from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FrameworkProfile:
    name: str
    control_flow: int
    role_modeling: int
    conversation: int
    state_resume: int
    operational_control: int
    notes: str


@dataclass(frozen=True)
class ProjectNeeds:
    control_flow: int = 1
    role_modeling: int = 1
    conversation: int = 1
    state_resume: int = 1
    operational_control: int = 1


PROFILES = (
    FrameworkProfile("LangGraph", 5, 3, 3, 5, 5, "Best fit for explicit stateful workflows."),
    FrameworkProfile("CrewAI", 3, 6, 3, 2, 3, "Best fit for role-oriented teams and task delegation."),
    FrameworkProfile("AutoGen", 3, 4, 5, 3, 3, "Best fit for conversational multi-agent experiments."),
    FrameworkProfile("No framework", 4, 2, 1, 3, 5, "Best fit when typed functions and queues are enough."),
)


def score(profile: FrameworkProfile, needs: ProjectNeeds) -> int:
    return (
        profile.control_flow * needs.control_flow
        + profile.role_modeling * needs.role_modeling
        + profile.conversation * needs.conversation
        + profile.state_resume * needs.state_resume
        + profile.operational_control * needs.operational_control
    )


def rank_frameworks(needs: ProjectNeeds, profiles: tuple[FrameworkProfile, ...] = PROFILES) -> list[tuple[str, int, str]]:
    ranked = [(profile.name, score(profile, needs), profile.notes) for profile in profiles]
    return sorted(ranked, key=lambda item: (-item[1], item[0]))


def recommendation(needs: ProjectNeeds) -> str:
    name, points, notes = rank_frameworks(needs)[0]
    return f"{name}: {points} points. {notes}"
