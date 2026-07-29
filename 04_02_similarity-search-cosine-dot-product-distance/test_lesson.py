import unittest
from metrics import cosine_similarity, dot_product, euclidean_distance, rank

class MetricTests(unittest.TestCase):
    def test_unit_vectors_align_cosine_and_dot(self):
        self.assertAlmostEqual(cosine_similarity([1,0],[0.8,0.6]), dot_product([1,0],[0.8,0.6]))
    def test_distance_sorts_ascending(self):
        self.assertEqual(rank([0,0], {"far":[3,0],"near":[1,0]}, "euclidean")[0][0], "near")
    def test_bad_dimensions_fail(self):
        with self.assertRaises(ValueError): euclidean_distance([1],[1,2])

if __name__ == "__main__": unittest.main()
