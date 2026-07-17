from episodic_memory import Episode, EpisodeStore, format_episode_context


store = EpisodeStore()
store.add(Episode("Refund request", "Approved without checking amount", "Escalation", "Check amount before approving.", ("billing", "refund")))
store.add(Episode("Password reset", "Verified identity first", "Resolved", "Verify identity before account changes.", ("security", "account")))

episodes = store.retrieve(("billing", "refund"))
print(format_episode_context(episodes))
