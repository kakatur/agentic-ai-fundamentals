import unittest

import numpy as np

from ann_search import ProductHnswSearch, _normalize, recall_at_k


class RecallAtKTests(unittest.TestCase):
    def test_full_partial_and_empty_ann_results(self):
        exact = ("a", "b", "c", "d", "e")
        self.assertEqual(recall_at_k(exact, exact), 1.0)
        self.assertEqual(recall_at_k(exact, ("a", "c", "x")), 0.4)
        self.assertEqual(recall_at_k(exact, ()), 0.0)

    def test_duplicate_ann_ids_do_not_inflate_recall(self):
        self.assertEqual(
            recall_at_k(("a", "b", "c", "d", "e"), ("a", "a", "b", "c", "d")),
            0.8,
        )

    def test_empty_or_duplicate_exact_results_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            recall_at_k((), ())
        with self.assertRaisesRegex(ValueError, "unique IDs"):
            recall_at_k(("a", "a"), ("a",))


class ProductHnswSearchTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(52)
        self.vectors = rng.normal(size=(40, 8)).astype("float32")
        ids = [f"iphone-{i:02d}" for i in range(20)]
        ids.extend(f"android-{i:02d}" for i in range(20))
        products = ["iPhone App"] * 20 + ["Android App"] * 20
        self.search = ProductHnswSearch(
            ids, products, self.vectors, neighbors=4, ef_search=16
        )

    def test_duplicate_record_ids_are_rejected(self):
        duplicate_ids = ["same-id", "same-id"]
        products = ["iPhone App", "iPhone App"]
        vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype="float32")
        with self.assertRaisesRegex(ValueError, "record IDs must be unique"):
            ProductHnswSearch(duplicate_ids, products, vectors)

    def test_exact_and_ann_results_use_the_requested_product_and_k(self):
        result = self.search.compare(self.vectors[0], product="iPhone App", k=5)
        self.assertEqual(len(result.exact_ids), 5)
        self.assertEqual(len(result.ann_ids), 5)
        self.assertTrue(all(record_id.startswith("iphone-") for record_id in result.exact_ids))
        self.assertTrue(all(record_id.startswith("iphone-") for record_id in result.ann_ids))
        self.assertEqual(result.recall, recall_at_k(result.exact_ids, result.ann_ids))

    def test_invalid_product_k_dimension_and_zero_query_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown product"):
            self.search.compare(self.vectors[0], product="Windows", k=5)
        with self.assertRaisesRegex(ValueError, "k must be positive"):
            self.search.compare(self.vectors[0], product="iPhone App", k=0)
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            self.search.compare(self.vectors[0], product="iPhone App", k=21)
        with self.assertRaisesRegex(ValueError, "dimension"):
            self.search.compare(np.ones(7, dtype="float32"), product="iPhone App", k=5)
        with self.assertRaisesRegex(ValueError, "nonzero"):
            self.search.compare(np.zeros(8, dtype="float32"), product="iPhone App", k=5)

    def test_zero_or_non_finite_index_vectors_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "nonzero"):
            _normalize(np.array([[0.0, 0.0]], dtype="float32"))
        with self.assertRaisesRegex(ValueError, "finite"):
            _normalize(np.array([[np.nan, 1.0]], dtype="float32"))


if __name__ == "__main__":
    unittest.main()
