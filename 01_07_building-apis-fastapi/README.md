# Build and Test a Python API With FastAPI

Build a local FastAPI endpoint that accepts text and returns its word count. Test a valid request and invalid input with FastAPI's `TestClient`; the demo does not start a network server or call an AI model.

## Define the request and response

`TaskRequest` requires a `text` string with at least one character. `TaskResponse` defines the returned text and integer `word_count`. The minimum length check rejects an empty string but accepts whitespace-only text; `count_words` returns zero for whitespace. If that is not suitable for an application, add a validation rule.

## Create the endpoint

`@app.post('/tasks', response_model=TaskResponse)` registers a POST route. FastAPI parses and validates the request body, calls `create_task` with a `TaskRequest`, and uses the response model for the output. The route delegates counting to the plain Python function `count_words`, which splits on whitespace.

For `{"text": "My order arrived"}`, the result is HTTP 200 with:

```json
{"text": "My order arrived", "word_count": 3}
```

An empty string or missing `text` produces HTTP 422 for this endpoint before the route processes the request. The example has no authentication, persistence, or AI model integration; those require separate design.

## Test without a network server

The demo creates `TestClient(app)` and calls `client.post('/tasks', json=payload)`. It prints each request, status, and response. Tests assert the successful response and invalid-request status. The client exercises the app locally; it does not prove network-server or deployment behavior. An ASGI server such as Uvicorn is needed to serve real network traffic.

## Interview questions

- **Basic:** What does a route do? It maps an HTTP method and path to a handler.
- **Intermediate:** Why use a request model? It describes the expected input and lets FastAPI validate it before the handler uses it.
- **Advanced:** What does a `TestClient` test leave unverified? It can exercise the application locally but does not establish network, reverse proxy, authentication, or deployment behavior.

## Run and test

Requires Python 3.10 or newer. These commands use the tested FastAPI and TestClient dependencies; activation shown for macOS/Linux.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python demo.py
python -m unittest -v
```

Try a valid string, an empty string, and a missing `text` field. Verified with FastAPI 0.162.4 and httpx2 2.16.0.

References: FastAPI testing [https://fastapi.tiangolo.com/tutorial/testing/]; Starlette TestClient [https://www.starlette.dev/testclient/].
