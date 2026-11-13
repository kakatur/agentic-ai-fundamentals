"""Offline demo: simulate the server with a Requests response object."""
import requests
from api_client import fetch_order


class FakeSession:
    def get(self, url, *, params, timeout):
        print('GET:', url, 'params:', params, 'timeout:', timeout)
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"status":"shipped"}'
        return response


if __name__ == '__main__':
    print('Response:', fetch_order('https://example.test', 'A17', FakeSession()))
