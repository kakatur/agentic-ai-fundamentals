import unittest
from unittest.mock import Mock
import requests
from api_client import fetch_order


class ApiTests(unittest.TestCase):
    def test_request_and_success(self):
        response = Mock()
        response.json.return_value = {'status': 'shipped'}
        client = Mock()
        client.get.return_value = response
        self.assertEqual(fetch_order('https://example.test', 'A17', client), {'status': 'shipped'})
        client.get.assert_called_once_with('https://example.test/orders', params={'id': 'A17'}, timeout=5)
        response.raise_for_status.assert_called_once()

    def test_http_failure_and_timeout_propagate(self):
        client = Mock()
        client.get.return_value.raise_for_status.side_effect = requests.HTTPError('bad status')
        with self.assertRaises(requests.HTTPError):
            fetch_order('https://example.test', 'A17', client)
        client.get.side_effect = requests.Timeout('timed out')
        with self.assertRaises(requests.Timeout):
            fetch_order('https://example.test', 'A17', client)

    def test_bad_json_and_wrong_shape(self):
        client = Mock()
        client.get.return_value.json.side_effect = requests.exceptions.JSONDecodeError('bad', 'x', 0)
        with self.assertRaises(requests.exceptions.JSONDecodeError):
            fetch_order('https://example.test', 'A17', client)
        client.get.return_value.json.side_effect = None
        client.get.return_value.json.return_value = {'status': 2}
        with self.assertRaises(ValueError):
            fetch_order('https://example.test', 'A17', client)


if __name__ == '__main__':
    unittest.main()
