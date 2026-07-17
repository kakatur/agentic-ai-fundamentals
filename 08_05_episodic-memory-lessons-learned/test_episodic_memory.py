from episodic_memory import Episode, EpisodeStore, format_episode_context


def test_retrieve_returns_tag_related_episodes():
    store = EpisodeStore()
    billing = Episode("refund", "checked invoice", "approved", "Check invoice first.", ("billing", "refund"))
    security = Episode("login", "reset password", "resolved", "Verify identity.", ("security",))
    store.add(billing)
    store.add(security)
    assert store.retrieve(("billing",)) == (billing,)


def test_lessons_are_deduplicated():
    store = EpisodeStore()
    store.add(Episode("a", "x", "ok", "Ask for account ID.", ("support",)))
    store.add(Episode("b", "y", "ok", "Ask for account ID.", ("support",)))
    assert store.lessons_for(("support",)) == ("Ask for account ID.",)


def test_format_episode_context_includes_outcome_and_lesson():
    text = format_episode_context((Episode("task", "action", "outcome", "lesson"),))
    assert "Outcome: outcome" in text
    assert "Lesson: lesson" in text
