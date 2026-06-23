"""Decision support for choosing an agent architecture.

The rules are deliberately explicit and deterministic. They are not a benchmark
or a universal scoring formula; they turn architectural evidence into a
reviewable recommendation and identify what should be measured next.
"""

from dataclasses import dataclass
from enum import StrEnum


class Architecture(StrEnum):
    DETERMINISTIC = "deterministic_workflow"
    SINGLE_AGENT = "single_agent_with_tools"
    MULTI_AGENT = "multi_agent"


@dataclass(frozen=True)
class UseCase:
    name: str
    ambiguous_judgment: bool
    changing_or_unstructured_input: bool
    stable_rules_cover_task: bool
    independent_parallel_branches: int = 0
    needs_context_isolation: bool = False
    needs_specialized_permissions: bool = False
    needs_independent_verification: bool = False
    tool_confusion_persists: bool = False
    branches_share_most_context: bool = False
    branches_have_tight_dependencies: bool = False
    strict_latency_budget: bool = False
    task_value_supports_extra_cost: bool = False


@dataclass(frozen=True)
class Recommendation:
    architecture: Architecture
    reasons: tuple[str, ...]
    risks: tuple[str, ...]
    next_experiments: tuple[str, ...]


def recommend_architecture(use_case: UseCase) -> Recommendation:
    """Return the simplest architecture justified by the supplied evidence."""

    if (
        use_case.stable_rules_cover_task
        and not use_case.ambiguous_judgment
        and not use_case.changing_or_unstructured_input
    ):
        return Recommendation(
            architecture=Architecture.DETERMINISTIC,
            reasons=(
                "Stable rules cover the task.",
                "The workflow does not require ambiguous, context-sensitive judgment.",
            ),
            risks=(
                "Adding an LLM would introduce cost and nondeterminism without a clear benefit.",
            ),
            next_experiments=(
                "Test rule coverage against real edge cases before adding an agent.",
            ),
        )

    multi_agent_signals = _multi_agent_signals(use_case)
    coordination_penalties = _coordination_penalties(use_case)

    multi_agent_is_justified = (
        len(multi_agent_signals) >= 2
        and use_case.task_value_supports_extra_cost
        and len(coordination_penalties) <= 1
    )

    if multi_agent_is_justified:
        return Recommendation(
            architecture=Architecture.MULTI_AGENT,
            reasons=tuple(multi_agent_signals),
            risks=tuple(coordination_penalties)
            or ("Coordination, tracing, and evaluation remain more complex.",),
            next_experiments=(
                "Compare task success, latency, and total model usage with a single-agent baseline.",
                "Test handoff contracts and partial-failure behavior.",
                "Trace each agent separately and evaluate the final system outcome.",
            ),
        )

    reasons = [
        "A single agent is the default when agentic judgment is useful.",
        "The evidence does not yet justify distributing control across agents.",
    ]
    if multi_agent_signals:
        reasons.append(
            "Some multi-agent signals exist, but they are not strong enough to outweigh coordination cost."
        )

    risks = list(coordination_penalties)
    if use_case.tool_confusion_persists:
        risks.append("The current agent still confuses overlapping tools.")
    if not use_case.task_value_supports_extra_cost:
        risks.append("The task value does not yet justify extra model calls and operations.")

    return Recommendation(
        architecture=Architecture.SINGLE_AGENT,
        reasons=tuple(reasons),
        risks=tuple(risks)
        or ("A growing prompt or tool surface may eventually require decomposition.",),
        next_experiments=(
            "Improve tool names, descriptions, and argument schemas.",
            "Use dynamic tool selection or load specialized context on demand.",
            "Establish a measured single-agent baseline before adding agents.",
        ),
    )


def _multi_agent_signals(use_case: UseCase) -> list[str]:
    signals: list[str] = []

    if use_case.independent_parallel_branches >= 2:
        signals.append(
            f"{use_case.independent_parallel_branches} independent branches can run in parallel."
        )
    if use_case.needs_context_isolation:
        signals.append("Specialists need separate context to avoid irrelevant information.")
    if use_case.needs_specialized_permissions:
        signals.append("Capabilities require distinct tools, permissions, or ownership boundaries.")
    if use_case.needs_independent_verification:
        signals.append("The result benefits from an independent producer-verifier boundary.")
    if use_case.tool_confusion_persists:
        signals.append("Tool-selection errors persist after improving the tool interfaces.")

    return signals


def _coordination_penalties(use_case: UseCase) -> list[str]:
    penalties: list[str] = []

    if use_case.branches_share_most_context:
        penalties.append("Agents would repeatedly copy and reconcile mostly shared context.")
    if use_case.branches_have_tight_dependencies:
        penalties.append("Tight dependencies limit useful parallelism and increase handoff risk.")
    if use_case.strict_latency_budget:
        penalties.append("A strict latency budget makes extra orchestration risky.")

    return penalties

