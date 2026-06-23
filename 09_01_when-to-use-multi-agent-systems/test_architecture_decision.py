import unittest

from architecture_decision import Architecture, UseCase, recommend_architecture


class ArchitectureDecisionTests(unittest.TestCase):
    def test_stable_rules_choose_deterministic_workflow(self) -> None:
        decision = recommend_architecture(
            UseCase(
                name="Invoice export",
                ambiguous_judgment=False,
                changing_or_unstructured_input=False,
                stable_rules_cover_task=True,
            )
        )

        self.assertEqual(decision.architecture, Architecture.DETERMINISTIC)

    def test_agentic_task_defaults_to_one_agent(self) -> None:
        decision = recommend_architecture(
            UseCase(
                name="Support assistant",
                ambiguous_judgment=True,
                changing_or_unstructured_input=True,
                stable_rules_cover_task=False,
                task_value_supports_extra_cost=True,
            )
        )

        self.assertEqual(decision.architecture, Architecture.SINGLE_AGENT)

    def test_one_multi_agent_signal_is_not_enough(self) -> None:
        decision = recommend_architecture(
            UseCase(
                name="Large-context analysis",
                ambiguous_judgment=True,
                changing_or_unstructured_input=True,
                stable_rules_cover_task=False,
                needs_context_isolation=True,
                task_value_supports_extra_cost=True,
            )
        )

        self.assertEqual(decision.architecture, Architecture.SINGLE_AGENT)

    def test_parallel_isolated_high_value_work_can_choose_multi_agent(self) -> None:
        decision = recommend_architecture(
            UseCase(
                name="Due diligence",
                ambiguous_judgment=True,
                changing_or_unstructured_input=True,
                stable_rules_cover_task=False,
                independent_parallel_branches=4,
                needs_context_isolation=True,
                needs_independent_verification=True,
                task_value_supports_extra_cost=True,
            )
        )

        self.assertEqual(decision.architecture, Architecture.MULTI_AGENT)
        self.assertTrue(any("parallel" in reason for reason in decision.reasons))

    def test_low_value_task_stays_single_agent(self) -> None:
        decision = recommend_architecture(
            UseCase(
                name="Low-value summary",
                ambiguous_judgment=True,
                changing_or_unstructured_input=True,
                stable_rules_cover_task=False,
                independent_parallel_branches=3,
                needs_context_isolation=True,
                task_value_supports_extra_cost=False,
            )
        )

        self.assertEqual(decision.architecture, Architecture.SINGLE_AGENT)
        self.assertTrue(any("task value" in risk.lower() for risk in decision.risks))

    def test_multiple_coordination_penalties_keep_one_agent(self) -> None:
        decision = recommend_architecture(
            UseCase(
                name="Tightly coupled incident response",
                ambiguous_judgment=True,
                changing_or_unstructured_input=True,
                stable_rules_cover_task=False,
                independent_parallel_branches=3,
                needs_specialized_permissions=True,
                branches_share_most_context=True,
                branches_have_tight_dependencies=True,
                strict_latency_budget=True,
                task_value_supports_extra_cost=True,
            )
        )

        self.assertEqual(decision.architecture, Architecture.SINGLE_AGENT)
        self.assertGreaterEqual(len(decision.risks), 3)


if __name__ == "__main__":
    unittest.main()

