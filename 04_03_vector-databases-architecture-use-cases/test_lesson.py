import unittest
from vector_store import ExactVectorStore, Record
class StoreTests(unittest.TestCase):
    def setUp(self): self.store=ExactVectorStore(2,"v1")
    def test_upsert_replaces_and_delete_removes(self):
        self.store.upsert(Record("a","old",(1,0),"t","v1")); self.store.upsert(Record("a","new",(0,1),"t","v1"))
        self.assertEqual(self.store.query((0,1),"t")[0][0],"a"); self.store.delete("a"); self.assertEqual(self.store.query((0,1),"t"),[])
    def test_tenant_filter_precedes_ranking(self):
        self.store.upsert(Record("x","x",(1,0),"other","v1")); self.assertEqual(self.store.query((1,0),"mine"),[])
    def test_version_mismatch_fails(self):
        with self.assertRaises(ValueError): self.store.upsert(Record("x","x",(1,0),"t","v2"))
if __name__ == "__main__": unittest.main()
