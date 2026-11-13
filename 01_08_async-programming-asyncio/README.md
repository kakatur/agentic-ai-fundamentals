# Python asyncio: Run Independent AI Requests Concurrently

Use `async` and `await` to simulate two independent I/O operations, compare sequential and concurrent execution, and handle a timeout. The example uses `asyncio.sleep` to simulate waiting; it does not call an AI model or a remote API.

## Coroutines and await

`fetch_source` is declared with `async def`. Calling it creates a coroutine object; it runs when awaited or scheduled. It awaits `asyncio.sleep`, which suspends that coroutine and lets the event loop run other work while it waits.

`sequential` awaits the first simulated source before starting the second. Each waits 0.2 seconds, so the demo often takes around 0.4 seconds plus overhead. Actual times vary.

## Run independent operations concurrently

`concurrent` passes both coroutine objects to `asyncio.gather` and awaits the results. They can make progress while the other is waiting. Both waits are 0.2 seconds, so the local demo often takes around 0.2 seconds plus overhead. These numbers illustrate simulated waiting, not a benchmark or promise for real APIs. `gather` returns results in the order of its arguments, even if they finish in a different order.

This pattern is useful when operations are independent and the libraries cooperate with the event loop. Async does not make blocking code nonblocking or automatically speed up CPU-bound work. Account for service limits and resource use when choosing concurrency.

## Handle a timeout

`fetch_with_timeout` awaits `asyncio.wait_for`. If the simulated operation exceeds the limit, `wait_for` requests cancellation and raises `TimeoutError` after cancellation completes. The total time can exceed the nominal timeout while cancellation finishes. The demo catches the exception and reports the timeout. Cleanup should be designed for cancellation in real operations.

## Interview questions

- **Basic:** What does `await` do? It suspends the current coroutine while waiting for an awaitable, allowing the event loop to run other work.
- **Intermediate:** How does `gather` order results? Successful results are returned in the same order as the supplied awaitables, not necessarily completion order.
- **Advanced:** Does `asyncio.wait_for` always return exactly at its deadline? No. It requests cancellation on timeout and waits for cancellation to finish, so elapsed time may be longer.

## Run and test

Requires Python 3.11 or newer; no third-party packages are needed.

```bash
python3 demo.py
python3 -m unittest -v
```

Tests check result ordering, use an event to show both concurrent calls start before either is released, and exercise the timeout. The demo reports approximate elapsed times; expect variation.

Reference: Python asyncio tasks [https://docs.python.org/3/library/asyncio-task.html].
