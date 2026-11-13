import asyncio
from time import perf_counter
from async_agent_calls import concurrent, fetch_with_timeout, sequential


async def main():
    for label, operation in [('Sequential', sequential), ('Concurrent', concurrent)]:
        start = perf_counter()
        result = await operation()
        print(f'{label}: {result}; elapsed ~{perf_counter() - start:.2f}s')
    try:
        await fetch_with_timeout(0.2, 0.05)
    except TimeoutError:
        print('Slow source: timed out')


if __name__ == '__main__':
    asyncio.run(main())
