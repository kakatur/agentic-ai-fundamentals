import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from pydantic import ValidationError
from parse_response import parse_response, save_response


class ParseTests(unittest.TestCase):
    def test_valid_response_and_saved_roundtrip(self):
        response = parse_response('{"category":"shipping","summary":"On its way"}')
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'response.json'
            save_response(response, path)
            self.assertEqual(json.loads(path.read_text()), {'category': 'shipping', 'summary': 'On its way'})

    def test_invalid_json_is_distinct_from_invalid_shape(self):
        with self.assertRaises(json.JSONDecodeError):
            parse_response('{')
        for raw in ('{"category":"billing","summary":"x"}',
                    '{"category":"shipping"}',
                    '[]',
                    '{"category":"shipping","summary":"x","extra":1}'):
            with self.subTest(raw=raw), self.assertRaises(ValidationError):
                parse_response(raw)


if __name__ == '__main__':
    unittest.main()
