from retrieval_collections import build_index, rank_documents

docs = {'a': 'python async api', 'b': 'python data dict list', 'c': 'sql api'}
index = build_index(docs)
print(index)
print(rank_documents(['python', 'api'], docs))
