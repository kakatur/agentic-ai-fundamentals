from task_api import InMemoryTaskRepository, create_task_handler, list_tasks_handler

repo = InMemoryTaskRepository()
print(create_task_handler({'title': 'Review prompt', 'priority': 'high'}, repo))
print(list_tasks_handler(repo))
