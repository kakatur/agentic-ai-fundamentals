from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelResult:
    prompt: str
    answer: str


class FakeModelClient:
    def __init__(self, delay: float = 0.01) -> None:
        self.delay = delay

    async def complete(self, prompt: str) -> ModelResult:
        await asyncio.sleep(self.delay)
        return ModelResult(prompt=prompt, answer=prompt.upper())


async def answer_one(client: FakeModelClient, prompt: str, *, timeout: float = 1.0) -> ModelResult:
    return await asyncio.wait_for(client.complete(prompt), timeout=timeout)


async def answer_many(client: FakeModelClient, prompts: list[str], *, timeout: float = 1.0) -> list[ModelResult]:
    tasks = [answer_one(client, prompt, timeout=timeout) for prompt in prompts]
    return await asyncio.gather(*tasks)


async def answer_many_with_errors(client: FakeModelClient, prompts: list[str], *, timeout: float = 1.0) -> list[ModelResult | Exception]:
    tasks = [answer_one(client, prompt, timeout=timeout) for prompt in prompts]
    return await asyncio.gather(*tasks, return_exceptions=True)


async def bounded_answer_many(client: FakeModelClient, prompts: list[str], *, limit: int, timeout: float = 1.0) -> list[ModelResult]:
    semaphore = asyncio.Semaphore(limit)

    async def run(prompt: str) -> ModelResult:
        async with semaphore:
            return await answer_one(client, prompt, timeout=timeout)

    return await asyncio.gather(*(run(prompt) for prompt in prompts))
