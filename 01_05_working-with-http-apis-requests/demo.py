from api_client import APIClient, FakeTransport

transport = FakeTransport([{'status_code': 200, 'json': {'ok': True}}])
client = APIClient('https://example.test', token='dev-token', transport=transport)
print(client.get_json('/health'))
print(transport.calls)
