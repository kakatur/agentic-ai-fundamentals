from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class APIError(RuntimeError):
    pass


@dataclass(frozen=True)
class Response:
    status_code: int
    body: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return self.body


class Transport(Protocol):
    def get(self, url: str, *, headers: dict[str, str], timeout: float) -> Response:
        ...


class FakeTransport:
    def __init__(self, responses: list[dict[str, Any]]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def get(self, url: str, *, headers: dict[str, str], timeout: float) -> Response:
        self.calls.append({"url": url, "headers": headers, "timeout": timeout})
        if not self.responses:
            raise APIError("no fake response configured")
        item = self.responses.pop(0)
        return Response(status_code=item["status_code"], body=item.get("json", {}))


class APIClient:
    def __init__(self, base_url: str, *, token: str, transport: Transport, timeout: float = 5.0, retries: int = 2) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.transport = transport
        self.timeout = timeout
        self.retries = retries

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}

    def get_json(self, path: str) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        last_status = None
        for attempt in range(self.retries + 1):
            response = self.transport.get(url, headers=self._headers(), timeout=self.timeout)
            last_status = response.status_code
            if response.status_code == 429 or response.status_code >= 500:
                if attempt < self.retries:
                    continue
            if 200 <= response.status_code < 300:
                return response.json()
            raise APIError(f"GET {url} failed with status {response.status_code}")
        raise APIError(f"GET {url} failed after retries; last status {last_status}")
