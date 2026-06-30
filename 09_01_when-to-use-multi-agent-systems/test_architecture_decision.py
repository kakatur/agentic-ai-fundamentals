from architecture_decision import Architecture, WorkloadSignals, recommend_architecture


def test_stable_rules_choose_deterministic_workflow() -> None:
    decision = recommend_architecture(
        WorkloadSignals(
            name="Invoice export",
            stable_rules_cover_task=True,
            requires_model_judgment=False,
        )
    )

    assert decision.architecture == Architecture.DETERMINISTIC


def test_model_judgment_defaults_to_one_agent() -> None:
    decision = recommend_architecture(
        WorkloadSignals(
            name="Support assistant",
            stable_rules_cover_task=False,
            requires_model_judgment=True,
            high_value_task=True,
        )
    )

    assert decision.architecture == Architecture.SINGLE_AGENT


def test_one_multi_agent_signal_is_not_enough() -> None:
    decision = recommend_architecture(
        WorkloadSignals(
            name="Large context review",
            stable_rules_cover_task=False,
            requires_model_judgment=True,
            distinct_contexts=True,
            high_value_task=True,
        )
    )

    assert decision.architecture == Architecture.SINGLE_AGENT
    assert any("not yet justified" in risk for risk in decision.risks)


def test_parallel_isolated_high_value_work_can_choose_multi_agent() -> None:
    decision = recommend_architecture(
        WorkloadSignals(
            name="Due diligence",
            stable_rules_cover_task=False,
            requires_model_judgment=True,
            independent_branches=4,
            distinct_contexts=True,
            requires_independent_review=True,
            high_value_task=True,
        )
    )

    assert decision.architecture == Architecture.MULTI_AGENT
    assert any("branches" in reason for reason in decision.reasons)


def test_coordination_costs_block_multi_agent_design() -> None:
    decision = recommend_architecture(
        WorkloadSignals(
            name="Incident response",
            stable_rules_cover_task=False,
            requires_model_judgment=True,
            independent_branches=3,
            distinct_tools_or_permissions=True,
            shared_context_heavy=True,
            tightly_coupled_steps=True,
            strict_latency_budget=True,
            high_value_task=True,
        )
    )

    assert decision.architecture == Architecture.SINGLE_AGENT
    assert len(decision.risks) >= 3
