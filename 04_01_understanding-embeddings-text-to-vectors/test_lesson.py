import math
import unittest

from embeddings import EmbeddingConfig, TokenHashEmbedder, assert_compatible, dot


class EmbeddingTests(unittest.TestCase):
    def setUp(self):
        self.config = EmbeddingConfig(dimension=12)
        self.embedder = TokenHashEmbedder(self.config)

    def test_repeatable_and_fixed_length(self):
        first = self.embedder.embed("hello")
        self.assertEqual(first, self.embedder.embed("hello"))
        self.assertEqual(len(first), 12)

    def test_nonzero_vector_is_unit_length(self):
        vector = self.embedder.embed("reset password")
        self.assertAlmostEqual(math.sqrt(dot(vector, vector)), 1.0)

    def test_different_embedding_configurations_fail(self):
        other = EmbeddingConfig(model_version="v2", dimension=12)
        with self.assertRaises(ValueError):
            assert_compatible(self.config, other)

    def test_dimension_mismatch_fails(self):
        with self.assertRaises(ValueError):
            dot([1.0], [1.0, 2.0])


if __name__ == "__main__":
    unittest.main()
