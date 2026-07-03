import asyncio
from async_agent_calls import FakeModelClient, answer_many

async def main():
    client = FakeModelClient(delay=0.01)
    print(await answer_many(client, ['a', 'b', 'c']))

asyncio.run(main())
