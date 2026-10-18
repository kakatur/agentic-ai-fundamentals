import unittest

from vector_store import ExactVectorStore, VectorRecord


def record(record_id, product="iPhone App", text="source", embedding=(1.0, 0.0), version="demo-v1"):
    return VectorRecord(record_id, product, text, embedding, version)


class ExactVectorStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = ExactVectorStore(dimension=2, expected_embedding_version="demo-v1")

    def test_search_filters_by_product_before_ranking(self):
        self.store.upsert(record("public", "iPhone App", embedding=(0.8, 0.6)))
        self.store.upsert(record("private", "Android App", embedding=(1.0, 0.0)))
        hits = self.store.search((1.0, 0.0), product="iPhone App")
        self.assertEqual([item.record_id for item, _score in hits], ["public"])

    def test_upsert_replaces_the_record_with_the_same_id(self):
        self.store.upsert(record("iphone-reset-17", text="revision 12"))
        self.store.upsert(record("iphone-reset-17", text="revision 13", embedding=(0.9, 0.1)))
        hits = self.store.search((1.0, 0.0), product="iPhone App")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0][0].text, "revision 13")

    def test_delete_removes_the_record_from_search(self):
        self.store.upsert(record("iphone-reset-17"))
        self.assertTrue(self.store.delete("iphone-reset-17"))
        self.assertFalse(self.store.delete("iphone-reset-17"))
        self.assertEqual(self.store.search((1.0, 0.0), product="iPhone App"), [])

    def test_dimension_and_zero_query_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "dimension"):
            self.store.upsert(record("bad", embedding=(1.0,)))
        with self.assertRaisesRegex(ValueError, "zero"):
            self.store.search((0.0, 0.0), product="iPhone App")

    def test_upsert_rejects_a_different_embedding_version(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.store.upsert(record("wrong-version", version="demo-v2"))

    def test_zero_and_non_finite_record_embeddings_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonzero"):
            self.store.upsert(record("zero", embedding=(0.0, 0.0)))
        with self.assertRaisesRegex(ValueError, "finite"):
            self.store.upsert(record("nan", embedding=(float("nan"), 1.0)))

    def test_non_finite_query_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be finite"):
            self.store.search((float("inf"), 1.0), product="iPhone App")


if __name__ == "__main__":
    unittest.main()
