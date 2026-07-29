import unittest
from local_backends import SearchRecord, validate_batch, upsert_chroma
class Fake:
    def upsert(self, **payload): self.payload=payload
class AdapterTests(unittest.TestCase):
    def test_rejects_ragged_vectors(self):
        with self.assertRaises(ValueError): validate_batch([SearchRecord("a","a",[1],{}),SearchRecord("b","b",[1,2],{})])
    def test_chroma_payload_stays_aligned(self):
        fake=Fake(); upsert_chroma(fake,[SearchRecord("a","doc",[1,0],{"x":1})]); self.assertEqual(fake.payload["ids"],["a"]); self.assertEqual(fake.payload["documents"],["doc"])
if __name__ == "__main__": unittest.main()
