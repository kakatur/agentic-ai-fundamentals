from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    role: str
    content: str


@dataclass(frozen=True)
class ConversationWindow:
    pinned_facts: tuple[str, ...]
    messages: tuple[Message, ...]


def add_message(history: tuple[Message, ...], role: str, content: str) -> tuple[Message, ...]:
    if role not in {"user", "assistant", "system"}:
        raise ValueError("role must be user, assistant, or system")
    return history + (Message(role, content),)


def trim_to_recent_pairs(history: tuple[Message, ...], max_pairs: int) -> tuple[Message, ...]:
    if max_pairs < 1:
        raise ValueError("max_pairs must be at least 1")
    turns: list[tuple[Message, ...]] = []
    current: list[Message] = []

    for message in history:
        if message.role == "user" and current:
            turns.append(tuple(current))
            current = [message]
        else:
            current.append(message)
    if current:
        turns.append(tuple(current))

    kept = turns[-max_pairs:]
    return tuple(message for turn in kept for message in turn)


def build_conversation_window(
    history: tuple[Message, ...],
    pinned_facts: tuple[str, ...],
    max_pairs: int,
) -> ConversationWindow:
    return ConversationWindow(pinned_facts=pinned_facts, messages=trim_to_recent_pairs(history, max_pairs))


def render_window(window: ConversationWindow) -> str:
    parts: list[str] = []
    if window.pinned_facts:
        parts.append("PINNED FACTS:\n" + "\n".join(f"- {fact}" for fact in window.pinned_facts))
    parts.append("RECENT CONVERSATION:")
    parts.extend(f"{message.role.upper()}: {message.content}" for message in window.messages)
    return "\n".join(parts)
