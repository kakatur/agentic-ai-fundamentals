"""Run representative architecture decisions."""

from architecture_decision import WorkloadSignals, recommend_architecture


SCENARIOS = (
    WorkloadSignals(
        name="Nightly invoice export",
        stable_rules_cover_task=True,
        requires_model_judgment=False,
    ),
    WorkloadSignals(
        name="Support assistant with tools",
        stable_rules_cover_task=False,
        requires_model_judgment=True,
        shared_context_heavy=True,
        strict_latency_budget=True,
    ),
    WorkloadSignals(
        name="Cross-market diligence report",
        stable_rules_cover_task=False,
        requires_model_judgment=True,
        independent_branches=4,
        distinct_contexts=True,
        requires_independent_review=True,
        high_value_task=True,
    ),
)


def main() -> None:
    for scenario in SCENARIOS:
        decision = recommend_architecture(scenario)
        print(f"\n{scenario.name}")
        print(f"  recommendation: {decision.architecture.value}")
        for reason in decision.reasons:
            print(f"  - {reason}")


if __name__ == "__main__":
    main()
