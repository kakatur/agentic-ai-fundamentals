"""Run representative architecture decisions."""

from architecture_decision import UseCase, recommend_architecture


SCENARIOS = (
    UseCase(
        name="Nightly invoice export",
        ambiguous_judgment=False,
        changing_or_unstructured_input=False,
        stable_rules_cover_task=True,
    ),
    UseCase(
        name="Customer support assistant",
        ambiguous_judgment=True,
        changing_or_unstructured_input=True,
        stable_rules_cover_task=False,
        tool_confusion_persists=False,
        branches_share_most_context=True,
        strict_latency_budget=True,
        task_value_supports_extra_cost=False,
    ),
    UseCase(
        name="Cross-market due-diligence report",
        ambiguous_judgment=True,
        changing_or_unstructured_input=True,
        stable_rules_cover_task=False,
        independent_parallel_branches=4,
        needs_context_isolation=True,
        needs_independent_verification=True,
        task_value_supports_extra_cost=True,
    ),
)


def main() -> None:
    for scenario in SCENARIOS:
        decision = recommend_architecture(scenario)
        print(f"\n{scenario.name}")
        print(f"  recommendation: {decision.architecture}")
        for reason in decision.reasons:
            print(f"  - {reason}")


if __name__ == "__main__":
    main()

