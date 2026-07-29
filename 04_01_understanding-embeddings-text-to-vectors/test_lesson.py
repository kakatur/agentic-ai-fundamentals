import math
import unittest
from embeddings import EmbeddingConfig, TokenHashEmbedder, dot

class EmbeddingTests(unittest.TestCase):
    def setUp(self): self.embedder = TokenHashEmbedder(EmbeddingConfig(dimension=12))
    def test_repeatable_and_fixed_length(self):
        self.assertEqual(self.embedder.embed("hello"), self.embedder.embed("hello"))
        self.assertEqual(len(self.embedder.embed("hello")), 12)
    def test_nonzero_vector_is_unit_length(self):
        vector = self.embedder.embed("reset password")
        self.assertAlmostEqual(math.sqrt(dot(vector, vector)), 1.0)
    def test_dimension_mismatch_fails(self):
        with self.assertRaises(ValueError): dot([1.0], [1.0, 2.0])

if __name__ == "__main__": unittest.main()
