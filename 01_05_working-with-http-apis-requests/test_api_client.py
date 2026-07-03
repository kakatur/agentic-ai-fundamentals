import pytest

from api_client import APIClient, APIError, FakeTransport


def test_client_sends_auth_header_and_timeout():
    transport = FakeTransport([{"status_code": 200, "json": {"ok": True}}])
    client = APIClient("https://api.example", token="abc", transport=transport, timeout=2.5)
    assert client.get_json("/health") == {"ok": True}
    assert transport.calls[0]["headers"]["Authorization"] == "Bearer abc"
    assert transport.calls[0]["timeout"] == 2.5


def test_client_retries_rate_limit_then_succeeds():
    transport = FakeTransport([
        {"status_code": 429, "json": {"error": "slow down"}},
        {"status_code": 200, "json": {"ok": True}},
    ])
    client = APIClient("https://api.example", token="abc", transport=transport, retries=1)
    assert client.get_json("items") == {"ok": True}
    assert len(transport.calls) == 2


def test_client_raises_after_non_retryable_error():
    transport = FakeTransport([{"status_code": 401, "json": {"error": "bad token"}}])
    client = APIClient("https://api.example", token="bad", transport=transport)
    with pytest.raises(APIError, match="401"):
        client.get_json("/items")
