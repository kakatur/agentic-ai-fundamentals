from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Task:
    id: int
    title: str
    priority: str
    done: bool = False


class TaskRepository(Protocol):
    def create(self, title: str, priority: str) -> Task:
        ...

    def list(self) -> list[Task]:
        ...


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._items: list[Task] = []

    def create(self, title: str, priority: str) -> Task:
        task = Task(id=len(self._items) + 1, title=title, priority=priority)
        self._items.append(task)
        return task

    def list(self) -> list[Task]:
        return list(self._items)


def validate_payload(payload: dict[str, str]) -> tuple[str, str]:
    title = payload.get("title", "").strip()
    priority = payload.get("priority", "normal")
    if not title:
        raise ValueError("title is required")
    if priority not in {"low", "normal", "high"}:
        raise ValueError("priority must be low, normal, or high")
    return title, priority


def create_task_handler(payload: dict[str, str], repo: TaskRepository) -> dict[str, object]:
    title, priority = validate_payload(payload)
    task = repo.create(title=title, priority=priority)
    return {"id": task.id, "title": task.title, "priority": task.priority, "done": task.done}


def list_tasks_handler(repo: TaskRepository) -> list[dict[str, object]]:
    return [
        {"id": task.id, "title": task.title, "priority": task.priority, "done": task.done}
        for task in repo.list()
    ]


def build_fastapi_app():
    try:
        from fastapi import Depends, FastAPI, HTTPException
        from pydantic import BaseModel
    except ImportError as exc:
        raise RuntimeError("Install requirements.txt to run the FastAPI server") from exc

    class TaskCreate(BaseModel):
        title: str
        priority: str = "normal"

    app = FastAPI(title="Task API")
    repo = InMemoryTaskRepository()

    def get_repo() -> TaskRepository:
        return repo

    @app.post("/tasks", status_code=201)
    def create_task(payload: TaskCreate, task_repo: TaskRepository = Depends(get_repo)):
        try:
            return create_task_handler(payload.model_dump(), task_repo)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/tasks")
    def list_tasks(task_repo: TaskRepository = Depends(get_repo)):
        return list_tasks_handler(task_repo)

    return app


try:
    app = build_fastapi_app()
except RuntimeError:
    app = None
