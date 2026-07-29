from embeddings import EmbeddingConfig, TokenHashEmbedder, dot

embedder = TokenHashEmbedder(EmbeddingConfig())
query = embedder.embed("reset password")
for text in ["password reset", "quarterly revenue", "reset account password"]:
    print(f"{dot(query, embedder.embed(text)):+.3f}  {text}")
