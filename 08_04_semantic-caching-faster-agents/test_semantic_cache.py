from semantic_cache import SemanticCache, cosine_similarity, tokenize


def test_tokenize_normalizes_words():
    assert tokenize("Reset, my PASSWORD!") == ["reset", "my", "password"]


def test_cosine_similarity_scores_related_text_higher():
    related = cosine_similarity("reset password account", "password reset help")
    unrelated = cosine_similarity("reset password account", "shipping label invoice")
    assert related > unrelated


def test_cache_returns_hit_above_threshold():
    cache = SemanticCache(threshold=0.4)
    cache.add("reset password account", "Use the reset flow.", "support")
    hit = cache.lookup("account password reset", "support")
    assert hit is not None
    assert hit.entry.response == "Use the reset flow."


def test_cache_respects_safety_label():
    cache = SemanticCache(threshold=0.1)
    cache.add("delete my account", "Here is the deletion workflow.", "privacy")
    assert cache.lookup("delete account", "general") is None
