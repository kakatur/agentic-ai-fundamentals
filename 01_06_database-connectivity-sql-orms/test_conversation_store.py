import sqlite3
import unittest
from conversation_store import add_messages, create_schema, get_messages


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        create_schema(self.db)

    def tearDown(self):
        self.db.close()

    def test_conversation_isolation_and_order(self):
        add_messages(self.db, "a' OR 1=1 --", [('user', 'one'), ('assistant', 'two')])
        add_messages(self.db, 'other', [('user', 'private')])
        self.assertEqual(get_messages(self.db, "a' OR 1=1 --"), [('user', 'one'), ('assistant', 'two')])
        self.assertEqual(get_messages(self.db, 'missing'), [])

    def test_invalid_row_rolls_back_batch(self):
        with self.assertRaises(sqlite3.IntegrityError):
            add_messages(self.db, 'a', [('user', 'one'), ('assistant', None)])
        self.assertEqual(get_messages(self.db, 'a'), [])


if __name__ == '__main__':
    unittest.main()
