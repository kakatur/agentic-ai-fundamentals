from embeddings import EmbeddingConfig, TokenHashEmbedder, assert_compatible, dot


config = EmbeddingConfig(dimension=16, normalize=True)
query_embedder = TokenHashEmbedder(config)
document_embedder = TokenHashEmbedder(config)
assert_compatible(query_embedder.config, document_embedder.config)

query = query_embedder.embed("reset password")
documents = ["password reset", "quarterly revenue", "reset account password"]

print(f"configuration: {config}")
print(f"vector dimension: {len(query)}")
for text in documents:
    score = dot(query, document_embedder.embed(text))
    print(f"{score:+.3f}  {text}")
