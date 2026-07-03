import pytest

from task_api import InMemoryTaskRepository, create_task_handler, list_tasks_handler, validate_payload


def test_validate_payload_checks_title_and_priority():
    assert validate_payload({"title": " Build API ", "priority": "high"}) == ("Build API", "high")
    with pytest.raises(ValueError):
        validate_payload({"title": "x", "priority": "urgent"})


def test_handlers_are_testable_without_http_server():
    repo = InMemoryTaskRepository()
    created = create_task_handler({"title": "Ship endpoint", "priority": "normal"}, repo)
    assert created == {"id": 1, "title": "Ship endpoint", "priority": "normal", "done": False}
    assert list_tasks_handler(repo) == [created]


def test_repository_returns_copy_not_internal_list():
    repo = InMemoryTaskRepository()
    repo.create("A", "low")
    items = repo.list()
    items.clear()
    assert len(repo.list()) == 1
