import unittest

from embeddings import EmbeddedText, cosine_similarity, embed_texts, exact_token_overlap, rank_documents


class FakeModel:
    """A tiny offline fixture for deterministic lesson tests."""

    vectors = {
        "I can't log in": [1.0, 0.0, 0.0],
        "Reset your password to regain account access.": [0.9, 0.1, 0.0],
        "Quarterly revenue": [0.0, 1.0, 0.0],
    }

    def encode_query(self, sentences, **kwargs):
        return [self.vectors[text] for text in sentences]

    def encode_document(self, sentences, **kwargs):
        return [self.vectors[text] for text in sentences]


class EmbeddingTests(unittest.TestCase):
    def setUp(self):
        self.model = FakeModel()

    def embed(self, texts, role):
        return embed_texts(self.model, texts, role=role, expected_dimension=3)

    def test_query_and_document_encoding(self):
        query = self.embed(["I can't log in"], "query")[0]
        document = self.embed(
            ["Reset your password to regain account access."], "document"
        )[0]
        self.assertEqual(query.role, "query")
        self.assertEqual(document.role, "document")
        self.assertGreater(cosine_similarity(query, document), 0.9)

    def test_keyword_baseline_has_no_overlap(self):
        self.assertEqual(
            exact_token_overlap(
                "I can't log in", "Reset your password to regain account access."
            ),
            set(),
        )

    def test_semantic_fixture_ranks_password_document_first(self):
        query = self.embed(["I can't log in"], "query")[0]
        documents = self.embed(
            ["Quarterly revenue", "Reset your password to regain account access."],
            "document",
        )
        ranking = rank_documents(query, documents)
        self.assertEqual(
            ranking[0][1].text, "Reset your password to regain account access."
        )

    def test_unexpected_model_output_dimension_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "expected 4 dimensions"):
            embed_texts(self.model, ["I can't log in"], role="query", expected_dimension=4)

    def test_vectors_must_have_equal_length(self):
        left = EmbeddedText("query", "query", (1.0, 0.0))
        right = EmbeddedText("document", "document", (1.0, 0.0, 0.0))
        with self.assertRaisesRegex(ValueError, "equal length"):
            cosine_similarity(left, right)

    def test_zero_vector_is_rejected(self):
        left = EmbeddedText("query", "query", (0.0, 0.0, 0.0))
        right = EmbeddedText("document", "document", (1.0, 0.0, 0.0))
        with self.assertRaisesRegex(ValueError, "zero vector"):
            cosine_similarity(left, right)

    def test_empty_text_and_unknown_role_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-empty"):
            self.embed([""], "query")
        with self.assertRaisesRegex(ValueError, "role"):
            self.embed(["I can't log in"], "passage")


if __name__ == "__main__":
    unittest.main()
