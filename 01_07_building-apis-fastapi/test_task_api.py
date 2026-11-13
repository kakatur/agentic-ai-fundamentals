import unittest
from fastapi.testclient import TestClient
from task_api import app, count_words


class TaskApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_valid_request_and_output(self):
        response = self.client.post('/tasks', json={'text': 'My order arrived'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'text': 'My order arrived', 'word_count': 3})

    def test_invalid_request(self):
        self.assertEqual(self.client.post('/tasks', json={'text': ''}).status_code, 422)
        self.assertEqual(self.client.post('/tasks', json={}).status_code, 422)

    def test_count_words_handles_whitespace(self):
        self.assertEqual(count_words(' a\n b '), 2)


if __name__ == '__main__':
    unittest.main()
