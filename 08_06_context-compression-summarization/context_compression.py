from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationFact:
    text: str
    kind: str
    priority: int


@dataclass(frozen=True)
class CompressedContext:
    constraints: tuple[str, ...]
    decisions: tuple[str, ...]
    open_tasks: tuple[str, ...]
    summary: str


def classify_line(line: str) -> ConversationFact:
    lowered = line.lower()
    if any(word in lowered for word in ("must", "never", "only", "require")):
        return ConversationFact(line, "constraint", 5)
    if any(word in lowered for word in ("decided", "chose", "approved")):
        return ConversationFact(line, "decision", 4)
    if any(word in lowered for word in ("todo", "next", "follow up")):
        return ConversationFact(line, "open_task", 4)
    return ConversationFact(line, "background", 1)


def compress_context(lines: list[str], max_background_items: int = 2) -> CompressedContext:
    facts = [classify_line(line.strip()) for line in lines if line.strip()]
    constraints = tuple(fact.text for fact in facts if fact.kind == "constraint")
    decisions = tuple(fact.text for fact in facts if fact.kind == "decision")
    open_tasks = tuple(fact.text for fact in facts if fact.kind == "open_task")
    background = [fact.text for fact in facts if fact.kind == "background"][:max_background_items]
    summary_parts = []
    if background:
        summary_parts.append("Background: " + " ".join(background))
    if decisions:
        summary_parts.append("Decisions: " + " ".join(decisions))
    if open_tasks:
        summary_parts.append("Open tasks: " + " ".join(open_tasks))
    return CompressedContext(constraints, decisions, open_tasks, " ".join(summary_parts))


def render_compressed_context(context: CompressedContext) -> str:
    sections = []
    if context.constraints:
        sections.append("NON-NEGOTIABLE CONSTRAINTS:\n" + "\n".join(f"- {item}" for item in context.constraints))
    sections.append("SUMMARY:\n" + context.summary)
    return "\n\n".join(sections)
