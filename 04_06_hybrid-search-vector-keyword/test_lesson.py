import unittest

from hybrid import reciprocal_rank_fusion


class ReciprocalRankFusionTests(unittest.TestCase):
    def test_reciprocal_ranks_can_promote_complementary_evidence(self):
        fused = reciprocal_rank_fusion(
            [["faq", "other", "runbook"], ["runbook", "faq"]],
            rank_constant=10,
        )
        self.assertEqual(fused[0][0], "faq")
        self.assertEqual({item[0] for item in fused}, {"faq", "other", "runbook"})

    def test_duplicate_id_contributes_only_at_its_first_rank_per_branch(self):
        fused = reciprocal_rank_fusion([["a", "a", "b"]], rank_constant=10)
        scores = dict(fused)
        self.assertAlmostEqual(scores["a"], 1 / 11)
        self.assertAlmostEqual(scores["b"], 1 / 13)

    def test_weights_must_match_the_number_of_rankings(self):
        with self.assertRaisesRegex(ValueError, "one weight"):
            reciprocal_rank_fusion([["a"], ["b"]], weights=[1.0])

    def test_weights_must_be_positive(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            reciprocal_rank_fusion([["a"]], weights=[0.0])


if __name__ == "__main__":
    unittest.main()
