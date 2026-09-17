import unittest

from vector_store import ExactVectorStore, Record


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.store = ExactVectorStore(2, "v1")

    def test_upsert_replaces_by_stable_id(self):
        self.store.upsert(Record("a", "old", (1, 0), "t", "v1"))
        self.store.upsert(Record("a", "new", (0, 1), "t", "v1"))
        self.assertEqual(self.store.query((0, 1), tenant_id="t")[0].text, "new")

    def test_tenant_and_metadata_define_eligibility(self):
        self.store.upsert(Record("x", "allowed", (1, 0), "mine", "v1", {"kind": "guide"}))
        self.store.upsert(Record("y", "wrong kind", (1, 0), "mine", "v1", {"kind": "invoice"}))
        self.store.upsert(Record("z", "wrong tenant", (1, 0), "other", "v1", {"kind": "guide"}))
        hits = self.store.query((1, 0), tenant_id="mine", metadata_filter={"kind": "guide"})
        self.assertEqual([hit.record_id for hit in hits], ["x"])

    def test_delete_removes_searchable_record(self):
        self.store.upsert(Record("a", "text", (1, 0), "t", "v1"))
        self.assertTrue(self.store.delete("a"))
        self.assertEqual(self.store.query((1, 0), tenant_id="t"), [])

    def test_invalid_vector_contract_fails(self):
        with self.assertRaises(ValueError):
            self.store.upsert(Record("x", "text", (1,), "t", "v1"))
        with self.assertRaises(ValueError):
            self.store.upsert(Record("x", "text", (1, 0), "t", "v2"))


if __name__ == "__main__":
    unittest.main()
