import unittest
from message_collections import count_by_role, latest_messages, make_history, sources_in_order


class CollectionsTests(unittest.TestCase):
    def test_latest_preserves_order_and_does_not_mutate_input(self):
        messages = [{"role": "user", "content": str(n)} for n in range(4)]
        self.assertEqual([m["content"] for m in latest_messages(messages, 2)], ["2", "3"])
        self.assertEqual(len(messages), 4)
        self.assertEqual(latest_messages([], 2), [])

    def test_limit_must_be_positive(self):
        with self.assertRaises(ValueError):
            latest_messages([], 0)

    def test_sources_remove_duplicates_without_losing_order(self):
        self.assertEqual(sources_in_order(["b", "a", "b", "c", "a"]), ["b", "a", "c"])
        self.assertEqual(sources_in_order([]), [])

    def test_role_counts_and_tuples(self):
        messages = [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"},
                    {"role": "user", "content": "bye"}]
        self.assertEqual(count_by_role(messages), {"user": 2, "assistant": 1})
        self.assertEqual(make_history(messages, 1), [("user", "bye")])


if __name__ == "__main__":
    unittest.main()
