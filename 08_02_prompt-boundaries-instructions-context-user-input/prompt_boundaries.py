from __future__ import annotations

from dataclasses import dataclass
from html import escape
from xml.etree import ElementTree


REQUIRED_SECTIONS = ("system_instructions", "trusted_context", "user_input")


@dataclass(frozen=True)
class PromptSection:
    name: str
    content: str

    def render(self) -> str:
        safe_text = escape(self.content.strip())
        return f"  <{self.name}>\n    {safe_text}\n  </{self.name}>"


@dataclass(frozen=True)
class BoundaryCheck:
    safe: bool
    warnings: tuple[str, ...] = ()


def build_prompt(system: str, context: str, user_input: str) -> str:
    sections = [
        PromptSection("system_instructions", system),
        PromptSection("trusted_context", context),
        PromptSection("user_input", user_input),
    ]
    rendered = "\n".join(section.render() for section in sections)
    return f"<prompt>\n{rendered}\n</prompt>"


def validate_prompt(prompt: str) -> None:
    try:
        root = ElementTree.fromstring(prompt)
    except ElementTree.ParseError as exc:
        raise ValueError("prompt boundaries are malformed") from exc

    names = tuple(section.tag for section in root)
    if root.tag != "prompt" or names != REQUIRED_SECTIONS:
        raise ValueError(
            "prompt must contain system_instructions, trusted_context, "
            "and user_input in that order"
        )


def check_input(user_input: str) -> BoundaryCheck:
    lowered = user_input.lower()
    warnings: list[str] = []
    phrases = [
        "ignore previous",
        "ignore the system",
        "you are now",
        "</system",
        "<system",
        "developer message",
    ]
    for phrase in phrases:
        if phrase in lowered:
            warnings.append(f"possible boundary attack: {phrase}")
    return BoundaryCheck(safe=not warnings, warnings=tuple(warnings))
