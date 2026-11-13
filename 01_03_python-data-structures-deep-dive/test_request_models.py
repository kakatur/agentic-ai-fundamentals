import unittest
from pydantic import ValidationError
from request_models import PlainRequest, SearchRequest


class RequestTests(unittest.TestCase):
    def test_dataclass_type_hints_do_not_validate(self):
        self.assertEqual(PlainRequest('hi', '3').max_results, '3')

    def test_strict_model_accepts_valid_data(self):
        request = SearchRequest.model_validate({'text': 'order', 'max_results': 3})
        self.assertEqual(request.model_dump(), {'text': 'order', 'max_results': 3})

    def test_bad_type_empty_text_extra_field_and_range_fail(self):
        for data in ({'text': 'order', 'max_results': '3'},
                     {'text': '', 'max_results': 3},
                     {'text': 'order', 'max_results': 11},
                     {'text': 'order', 'max_results': 3, 'extra': True}):
            with self.subTest(data=data), self.assertRaises(ValidationError):
                SearchRequest.model_validate(data)


if __name__ == '__main__':
    unittest.main()
