import unittest
from evaluation import Workload, Result, evaluate, comparable_scenarios
class EvaluationTests(unittest.TestCase):
    def test_all_constraints_must_pass(self):
        w=Workload(10,2,1,1,.5,1,5); checks,accepted=evaluate(w,Result("x",.9,20,2,10),min_recall=.95,max_p95_ms=50,max_cost=20); self.assertFalse(accepted); self.assertFalse(checks["recall"])
    def test_growth_scenario_is_explicit(self):
        w=Workload(10,2,1,1,.5,1,5); self.assertEqual(comparable_scenarios(w)["growth_3x"].vectors,30)
if __name__ == "__main__": unittest.main()
