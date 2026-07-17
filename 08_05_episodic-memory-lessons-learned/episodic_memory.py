from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Episode:
    task: str
    action: str
    outcome: str
    lesson: str
    tags: tuple[str, ...] = ()


def shared_tags(left: Episode, query_tags: tuple[str, ...]) -> int:
    return len(set(left.tags) & set(query_tags))


class EpisodeStore:
    def __init__(self) -> None:
        self._episodes: list[Episode] = []

    def add(self, episode: Episode) -> None:
        self._episodes.append(episode)

    def retrieve(self, query_tags: tuple[str, ...], limit: int = 3) -> tuple[Episode, ...]:
        ranked = sorted(
            self._episodes,
            key=lambda episode: (shared_tags(episode, query_tags), episode.task),
            reverse=True,
        )
        return tuple(episode for episode in ranked if shared_tags(episode, query_tags) > 0)[:limit]

    def lessons_for(self, query_tags: tuple[str, ...]) -> tuple[str, ...]:
        lessons: list[str] = []
        for episode in self.retrieve(query_tags):
            if episode.lesson not in lessons:
                lessons.append(episode.lesson)
        return tuple(lessons)


def format_episode_context(episodes: tuple[Episode, ...]) -> str:
    lines = []
    for episode in episodes:
        lines.append(f"Task: {episode.task}")
        lines.append(f"Action: {episode.action}")
        lines.append(f"Outcome: {episode.outcome}")
        lines.append(f"Lesson: {episode.lesson}")
        lines.append("")
    return "\n".join(lines).strip()
