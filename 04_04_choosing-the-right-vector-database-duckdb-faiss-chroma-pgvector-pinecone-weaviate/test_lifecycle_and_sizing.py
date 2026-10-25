"""Exercise real FAISS lifecycle/filtering and the interview storage calculation."""

import unittest

from local_backends import FaissAdapter, SearchRecord
from sizing import estimate_raw_vector_bytes


def article(record_id, embedding, product="billing", name="Example"):
    return SearchRecord(record_id, "Article body", embedding,
                        {"product": product}, "demo-v1", name)


class FaissLifecycleTests(unittest.TestCase):
    def test_upsert_replaces_vector_metadata_and_name_without_duplicate_id(self):
        store = FaissAdapter(2)
        store.upsert(article("article-1", (1.0, 0.0), name="Old"))
        store.upsert(article("article-2", (0.9, 0.1)))
        store.upsert(article("article-1", (0.0, 1.0), "account", "Updated"))
        all_hits = store.search((1.0, 0.0), filters={})
        self.assertEqual([hit.record_id for hit in all_hits], ["article-2", "article-1"])
        self.assertEqual(all_hits[1].name, "Updated")
        self.assertAlmostEqual(all_hits[1].score, 2.0)
        self.assertEqual([hit.record_id for hit in store.search(
            (1.0, 0.0), filters={"product": "billing"})], ["article-2"])

    def test_delete_removes_search_result_and_allows_reinsert(self):
        store = FaissAdapter(2)
        store.upsert(article("article-1", (1.0, 0.0)))
        self.assertTrue(store.delete("article-1"))
        self.assertFalse(store.delete("article-1"))
        self.assertEqual(store.search((1.0, 0.0), filters={}), [])
        store.upsert(article("article-1", (0.0, 1.0), name="Reinserted"))
        hits = store.search((0.0, 1.0), filters={})
        self.assertEqual([hit.record_id for hit in hits], ["article-1"])
        self.assertEqual(hits[0].name, "Reinserted")
        self.assertAlmostEqual(hits[0].score, 0.0)

    def test_filter_is_applied_before_limit_even_when_closest_records_are_excluded(self):
        store = FaissAdapter(2)
        for i in range(4):
            store.upsert(article(f"account-{i}", (1.0, i * 0.01), "account"))
        store.upsert(article("billing-1", (0.5, 0.5)))
        store.upsert(article("billing-2", (0.0, 1.0)))
        hits = store.search((1.0, 0.0), filters={"product": "billing"}, limit=2)
        self.assertEqual([hit.record_id for hit in hits], ["billing-1", "billing-2"])
        self.assertEqual(store.search((1.0, 0.0), filters={"product": "shipping"}), [])

    def test_invalid_queries_fail_before_search(self):
        store = FaissAdapter(2)
        for query in ((1.0,), (float("nan"), 0.0), (float("inf"), 0.0)):
            with self.subTest(query=query), self.assertRaises(ValueError):
                store.search(query, filters={})
        with self.assertRaises(ValueError):
            store.search((1.0, 0.0), filters={}, limit=0)


class StorageEstimateTests(unittest.TestCase):
    def test_interview_scenario_and_fivefold_growth(self):
        self.assertEqual(estimate_raw_vector_bytes(100_000_000, 1536), 614_400_000_000)
        self.assertEqual(estimate_raw_vector_bytes(500_000_000, 1536), 3_072_000_000_000)

    def test_zero_vectors_and_alternative_element_width(self):
        self.assertEqual(estimate_raw_vector_bytes(0, 1536), 0)
        self.assertEqual(estimate_raw_vector_bytes(100, 8, 2), 1600)

    def test_invalid_storage_inputs(self):
        for values in ((-1, 1536, 4), (1, 0, 4), (1, 3, 0),
                       (1.5, 3, 4), (True, 3, 4)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                estimate_raw_vector_bytes(*values)


if __name__ == "__main__":
    unittest.main()
