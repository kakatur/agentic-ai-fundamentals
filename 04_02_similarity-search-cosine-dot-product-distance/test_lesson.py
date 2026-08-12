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

    def test_dot_product_keeps_magnitude(self):
        self.assertAlmostEqual(dot_product([1, 0], [4, 0]), 4.0)

    def test_euclidean_measures_endpoint_gap(self):
        self.assertAlmostEqual(euclidean_distance([1, 0], [0.8, 0.2]), 2**0.5 / 5)

    def test_unit_vectors_make_cosine_and_dot_equal(self):
        left = l2_normalize([1, 0])
        right = l2_normalize([4, 3])
        self.assertAlmostEqual(cosine_similarity(left, right), dot_product(left, right))

    def test_normalized_vectors_have_the_same_metric_order(self):
        query = l2_normalize([1, 0])
        items = {
            "same": l2_normalize([4, 0]),
            "tilted": l2_normalize([4, 3]),
            "opposite": l2_normalize([-1, 0]),
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
