import asyncio
import unittest
from unittest.mock import patch
from async_agent_calls import concurrent, fetch_with_timeout, sequential


class AsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_results_are_ordered(self):
        self.assertEqual(await sequential(), ['orders: ready', 'shipping: ready'])
        self.assertEqual(await concurrent(), ['orders: ready', 'shipping: ready'])

    async def test_gather_starts_both_before_release(self):
        started = []
        release = asyncio.Event()
        async def fake_fetch(name, delay):
            started.append(name)
            if len(started) == 2:
                release.set()
            await release.wait()
            return name
        with patch('async_agent_calls.fetch_source', side_effect=fake_fetch):
            result = await asyncio.wait_for(concurrent(), timeout=1)
        self.assertEqual(result, ['orders', 'shipping'])

    async def test_timeout(self):
        with self.assertRaises(TimeoutError):
            await fetch_with_timeout(0.2, 0.01)


if __name__ == '__main__':
    unittest.main()
