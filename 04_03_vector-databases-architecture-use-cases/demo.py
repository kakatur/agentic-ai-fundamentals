from vector_store import ExactVectorStore, Record
store=ExactVectorStore(2,"embed-v1")
store.upsert(Record("a","reset password",(1.0,0.0),"acme","embed-v1"))
store.upsert(Record("b","billing",(0.0,1.0),"acme","embed-v1"))
store.upsert(Record("secret","other tenant",(1.0,0.0),"other","embed-v1"))
print(store.query((0.9,0.1),"acme"))
