"""Use Python collections to prepare conversation history and sources."""


def latest_messages(messages: list[dict], limit: int = 3) -> list[dict]:
    """Return up to limit recent messages in their original order."""
    if limit < 1:
        raise ValueError("limit must be positive")
    return messages[-limit:]


def sources_in_order(source_ids: list[str]) -> list[str]:
    """Remove duplicate IDs while retaining first-seen order."""
    seen = set()
    unique = []
    for source_id in source_ids:
        if source_id not in seen:
            seen.add(source_id)
            unique.append(source_id)
    return unique


def make_history(messages: list[dict], limit: int = 3) -> list[tuple[str, str]]:
    """Represent recent role/content pairs as tuples for display."""
    return [(message["role"], message["content"])
            for message in latest_messages(messages, limit)]


def count_by_role(messages: list[dict]) -> dict[str, int]:
    """Count messages for each role using dictionary lookup."""
    counts = {}
    for message in messages:
        role = message["role"]
        counts[role] = counts.get(role, 0) + 1
    return counts
