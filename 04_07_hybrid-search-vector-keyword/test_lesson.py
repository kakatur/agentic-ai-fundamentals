import unittest
from hybrid import reciprocal_rank_fusion, hybrid_search
class HybridTests(unittest.TestCase):
    def test_document_in_both_branches_rises(self):
        self.assertEqual(reciprocal_rank_fusion([["a","b"],["b","c"]])[0][0],"b")
    def test_ineligible_document_never_reaches_fusion(self):
        self.assertNotIn("secret",dict(hybrid_search(["secret","a"],["secret"],{"a"})))
    def test_bad_weights_fail(self):
        with self.assertRaises(ValueError): reciprocal_rank_fusion([["a"]],weights=[1,2])
if __name__ == "__main__": unittest.main()
