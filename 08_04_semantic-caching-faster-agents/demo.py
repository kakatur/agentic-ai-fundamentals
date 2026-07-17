from semantic_cache import SemanticCache


cache = SemanticCache(threshold=0.5)
cache.add("How do I reset my password?", "Open settings, choose Security, then Reset Password.", "support")

hit = cache.lookup("Can you help me reset a password?", "support")
if hit:
    print(f"Cache hit: {hit.score:.2f}")
    print(hit.entry.response)
else:
    print("Cache miss")
