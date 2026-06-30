"""Decision support for choosing an agent architecture.

The rules are deterministic on purpose. They do not replace product judgment;
they make the architectural evidence reviewable and testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Architecture(StrEnum):
    DETERMINISTIC = "deterministic_workflow"
    SINGLE_AGENT = "single_agent_with_tools"
    MULTI_AGENT = "multi_agent_system"


@dataclass(frozen=True)
class WorkloadSignals:
    name: str
    stable_rules_cover_task: bool
    requires_model_judgment: bool
    independent_branches: int = 0
    distinct_contexts: bool = False
    distinct_tools_or_permissions: bool = False
    requires_independent_review: bool = False
    single_agent_tool_confusion: bool = False
    shared_context_heavy: bool = False
    tightly_coupled_steps: bool = False
    strict_latency_budget: bool = False
    high_value_task: bool = False


@dataclass(frozen=True)
class ArchitectureDecision:
    architecture: Architecture
    reasons: tuple[str, ...]
    risks: tuple[str, ...]
    next_experiments: tuple[str, ...]


def recommend_architecture(workload: WorkloadSignals) -> ArchitectureDecision:
    """Choose the simplest architecture justified by the workload signals."""

    if workload.stable_rules_cover_task and not workload.requires_model_judgment:
        return ArchitectureDecision(
            architecture=Architecture.DETERMINISTIC,
            reasons=(
                "Stable rules cover the task.",
                "The workflow does not need model-driven judgment.",
            ),
            risks=("Adding an agent would add cost and nondeterminism.",),
            next_experiments=("Test rule coverage against edge cases.",),
        )

    benefits = _multi_agent_benefits(workload)
    costs = _coordination_costs(workload)
    justified = len(benefits) >= 2 and workload.high_value_task and len(costs) <= 1

    if justified:
        return ArchitectureDecision(
            architecture=Architecture.MULTI_AGENT,
            reasons=tuple(benefits),
            risks=tuple(costs) or ("Coordination and tracing are still required.",),
            next_experiments=(
                "Compare quality, latency, and model usage against one agent.",
                "Test handoff contracts and partial failure behavior.",
                "Trace each agent boundary separately.",
            ),
        )

    risks = list(costs)
    if benefits:
        risks.append("Multi-agent signals exist, but coordination cost is not yet justified.")
    if not workload.high_value_task:
        risks.append("The task value does not justify extra model calls and operations.")

    return ArchitectureDecision(
        architecture=Architecture.SINGLE_AGENT,
        reasons=(
            "Model judgment is useful, so an agent can help.",
            "One agent keeps state, tracing, and ownership simpler.",
        ),
        risks=tuple(risks) or ("A growing tool surface may eventually need decomposition.",),
        next_experiments=(
            "Improve tool descriptions and schemas.",
            "Load context and tools on demand.",
            "Measure the single-agent baseline before adding agents.",
        ),
    )


def _multi_agent_benefits(workload: WorkloadSignals) -> list[str]:
    benefits: list[str] = []

    if workload.independent_branches >= 2:
        benefits.append(f"{workload.independent_branches} branches can run independently.")
    if workload.distinct_contexts:
        benefits.append("Specialists need separate context windows.")
    if workload.distinct_tools_or_permissions:
        benefits.append("Tools, permissions, or ownership boundaries are distinct.")
    if workload.requires_independent_review:
        benefits.append("A separate reviewer can check the producer against evidence.")
    if workload.single_agent_tool_confusion:
        benefits.append("One agent still confuses tools after interface cleanup.")

    return benefits


def _coordination_costs(workload: WorkloadSignals) -> list[str]:
    costs: list[str] = []

    if workload.shared_context_heavy:
        costs.append("Agents would copy and reconcile mostly shared context.")
    if workload.tightly_coupled_steps:
        costs.append("Tight dependencies limit useful parallel work.")
    if workload.strict_latency_budget:
        costs.append("Extra handoffs may violate the latency budget.")

    return costs
