from collections import Counter

from retrieval_collections import build_index, rank_documents, summarize_collection_choice, tokenize


def test_tokenize_returns_ordered_list():
    assert tokenize("Python, Python API!") == ["python", "python", "api"]


def test_build_index_uses_sets_for_membership():
    index = build_index({"a": "python api", "b": "python sql"})
    assert index["python"] == {"a", "b"}
    assert index["api"] == {"a"}


def test_rank_documents_uses_tuple_scores_sorted_by_score():
    docs = {"a": "python api api", "b": "python sql", "c": "notes"}
    assert rank_documents(["python", "api"], docs) == [("a", 3), ("b", 1)]


def test_collection_summary_shows_different_semantics():
    summary = summarize_collection_choice(["tool", "agent", "tool"])
    assert summary["ordered_values"] == ["tool", "agent", "tool"]
    assert summary["unique_values"] == {"agent", "tool"}
    assert summary["counts"] == Counter({"tool": 2, "agent": 1})
    assert summary["first_and_last"] == ("tool", "tool")
