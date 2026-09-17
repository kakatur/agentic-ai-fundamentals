import unittest

from local_backends import SearchRecord, upsert_chroma, validate_batch


class FakeCollection:
    def upsert(self, **payload):
        self.payload = payload


class AdapterTests(unittest.TestCase):
    def test_rejects_ragged_vectors_and_duplicate_ids(self):
        with self.assertRaises(ValueError):
            validate_batch([SearchRecord("a", "a", [1], {}), SearchRecord("b", "b", [1, 2], {})])
        with self.assertRaises(ValueError):
            validate_batch([SearchRecord("a", "a", [1], {}), SearchRecord("a", "b", [2], {})])

    def test_chroma_payload_fields_stay_aligned(self):
        fake = FakeCollection()
        upsert_chroma(fake, [SearchRecord("a", "doc", [1, 0], {"team": "support"})])
        self.assertEqual(fake.payload["ids"], ["a"])
        self.assertEqual(fake.payload["documents"], ["doc"])
        self.assertEqual(fake.payload["embeddings"], [[1, 0]])
        self.assertEqual(fake.payload["metadatas"], [{"team": "support"}])


if __name__ == "__main__":
    unittest.main()
