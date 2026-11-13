"""Simulate independent I/O with asyncio; no model calls are made."""
import asyncio


async def fetch_source(name: str, delay: float) -> str:
    await asyncio.sleep(delay)
    return f'{name}: ready'


async def sequential() -> list[str]:
    first = await fetch_source('orders', 0.2)
    second = await fetch_source('shipping', 0.2)
    return [first, second]


async def concurrent() -> list[str]:
    return await asyncio.gather(fetch_source('orders', 0.2), fetch_source('shipping', 0.2))


async def fetch_with_timeout(delay: float, timeout: float) -> str:
    return await asyncio.wait_for(fetch_source('slow', delay), timeout=timeout)
