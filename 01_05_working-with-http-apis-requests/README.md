# Python HTTP Requests: Call an API and Handle Errors

Send an HTTP GET request with query parameters, check its status, decode JSON, and validate a response field. The demo uses a simulated response and makes no network request; tests exercise success and failure paths.

## Make the request

`fetch_order` asks the client for `/orders`, passing the order ID through `params` and setting `timeout=5`. With Requests, that timeout is not a five-second limit on the entire response download; it limits waiting for network activity, and connection and read timeout behavior should be chosen for the application. Requests does not time out by default when no timeout is provided.

The offline demo prints the URL, parameters, and timeout it receives:

```text
GET: https://example.test/orders params: {'id': 'A17'} timeout: 5
Response: {'status': 'shipped'}
```

`example.test` is an illustrative address. The demo's `FakeSession` supplies a simulated response rather than contacting it. In a real application, call `fetch_order` without the optional session and provide a real service URL.

## Check status before using JSON

`response.raise_for_status()` raises `requests.HTTPError` for unsuccessful HTTP responses. Next, `response.json()` decodes the body; a successful JSON decode does not imply a successful HTTP status. Invalid JSON can raise `requests.exceptions.JSONDecodeError`. Finally, the function checks that the decoded data is a dictionary with a string `status`.

A timeout or network error can also occur before a response arrives. This example lets these errors propagate so the caller can decide what to do. A production caller might report the error or retry a suitable operation; retries should account for whether repeating an operation is safe.

## Interview questions

- **Basic:** Why call `raise_for_status()`? It turns an unsuccessful HTTP status into an exception that the caller can handle.
- **Intermediate:** Does `response.json()` prove a request succeeded? No. An error response can itself contain valid JSON; inspect the HTTP status separately.
- **Advanced:** Is the Requests timeout a total deadline for the entire response? No. It controls connection and read waiting behavior rather than a total download deadline; choose appropriate limits for the application.

## Run and test

Requires Python 3.10 or newer and Requests 2. The commands below show macOS/Linux activation.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python demo.py
python -m unittest -v
```

Tests use a simulated client to check the URL, query parameters, timeout, unsuccessful status, timeout exception, malformed JSON, and invalid response shape. Verified with Requests 2.34.2.

Reference: Requests quickstart [https://requests.readthedocs.io/en/latest/user/quickstart/].
