import unittest

from metrics import (
    cosine_similarity,
    dot_product,
    euclidean_distance,
    l2_normalize,
    rank,
)


class MetricTests(unittest.TestCase):
    def test_cosine_ignores_length(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [4, 0]), 1.0)

    def test_cosine_rejects_zero_vectors(self):
        with self.assertRaisesRegex(ValueError, "undefined for zero vectors"):
            cosine_similarity([0, 0], [1, 0])
        with self.assertRaisesRegex(ValueError, "undefined for zero vectors"):
            cosine_similarity([1, 0], [0, 0])

    def test_l2_normalize_rejects_zero_vector(self):
        with self.assertRaisesRegex(ValueError, "zero vector"):
            l2_normalize([0, 0])

    def test_dot_product_keeps_magnitude(self):
        self.assertAlmostEqual(dot_product([1, 0], [4, 0]), 4.0)

    def test_euclidean_measures_endpoint_gap(self):
        self.assertAlmostEqual(euclidean_distance([1, 0], [0.8, 0.6]), 0.4**0.5)

    def test_shared_example_matches_lesson_rankings_and_scores(self):
        query = [1, 0]
        items = {
            "same direction": [4, 0],
            "diagonal": [5, 2],
            "nearby endpoint": [0.8, 0.6],
        }

        cosine_results = rank(query, items, "cosine")
        dot_results = rank(query, items, "dot")
        euclidean_results = rank(query, items, "euclidean")

        self.assertEqual([name for name, _ in cosine_results], ["same direction", "diagonal", "nearby endpoint"])
        self.assertEqual([name for name, _ in dot_results], ["diagonal", "same direction", "nearby endpoint"])
        self.assertEqual([name for name, _ in euclidean_results], ["nearby endpoint", "same direction", "diagonal"])
        self.assertAlmostEqual(cosine_results[0][1], 1.0)
        self.assertAlmostEqual(cosine_results[1][1], 5 / 29**0.5)
        self.assertAlmostEqual(cosine_results[2][1], 0.8)
        self.assertEqual([score for _, score in dot_results], [5.0, 4.0, 0.8])
        self.assertAlmostEqual(euclidean_results[0][1], 0.4**0.5)
        self.assertEqual(euclidean_results[1][1], 3.0)
        self.assertAlmostEqual(euclidean_results[2][1], 20**0.5)

    def test_unit_vectors_make_cosine_and_dot_equal(self):
        left = l2_normalize([1, 0])
        right = l2_normalize([4, 3])
        self.assertAlmostEqual(cosine_similarity(left, right), dot_product(left, right))

    def test_normalized_vectors_have_the_same_metric_order(self):
        query = l2_normalize([1, 0])
        items = {
            "same": l2_normalize([4, 0]),
            "diagonal": l2_normalize([5, 2]),
            "nearby": l2_normalize([0.8, 0.6]),
        }
        cosine_order = [name for name, _ in rank(query, items, "cosine")]
        dot_order = [name for name, _ in rank(query, items, "dot")]
        euclidean_order = [name for name, _ in rank(query, items, "euclidean")]
        self.assertEqual(cosine_order, dot_order)
        self.assertEqual(cosine_order, euclidean_order)

    def test_distance_sorts_ascending(self):
        results = rank([0, 0], {"far": [3, 0], "near": [1, 0]}, "euclidean")
        self.assertEqual(results[0][0], "near")

    def test_bad_dimensions_fail(self):
        with self.assertRaises(ValueError):
            euclidean_distance([1], [1, 2])

    def test_unknown_metric_fails(self):
        with self.assertRaises(ValueError):
            rank([1, 0], {"item": [1, 0]}, "unknown")


if __name__ == "__main__":
    unittest.main()
