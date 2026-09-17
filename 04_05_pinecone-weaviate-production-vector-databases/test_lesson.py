import unittest

from evaluation import Result, Workload, evaluate, growth_scenario


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.workload = Workload(10, 2, 1, 1, 0.5, 1, 5)

    def test_every_required_gate_must_pass(self):
        checks, accepted = evaluate(Result("x", 0.9, 20, 2, 10), self.workload, min_recall=0.95, max_p95_ms=50, max_cost=20)
        self.assertFalse(accepted)
        self.assertFalse(checks["recall"])

    def test_growth_scenario_preserves_original(self):
        grown = growth_scenario(self.workload)
        self.assertEqual(grown.vectors, 30)
        self.assertEqual(self.workload.vectors, 10)


if __name__ == "__main__":
    unittest.main()
