from fastapi.testclient import TestClient
from task_api import app

client = TestClient(app)
for payload in ({'text': 'My order arrived'}, {'text': ''}):
    response = client.post('/tasks', json=payload)
    print('Request:', payload)
    print('HTTP status:', response.status_code)
    print('Response:', response.json())
