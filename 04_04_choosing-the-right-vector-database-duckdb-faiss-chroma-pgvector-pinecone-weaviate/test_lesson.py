import unittest
import sys
from unittest.mock import patch

from local_backends import FaissAdapter, SearchRecord, validate_record


class FakeFaissIndex:
    def __init__(self, inner):
        self.rows = {}

    @property
    def ntotal(self):
        return len(self.rows)

    def add_with_ids(self, vectors, labels):
        for vector, label in zip(vectors, labels):
            self.rows[int(label)] = vector

    def remove_ids(self, labels):
        for label in labels:
            self.rows.pop(int(label), None)

    def search(self, queries, count):
        query = queries[0]
        ranked = sorted(
            (sum((left - right) ** 2 for left, right in zip(query, vector)), label)
            for label, vector in self.rows.items()
        )[:count]
        distances = [[float("inf") for _ in range(count)]]
        labels = [[-1 for _ in range(count)]]
        for index, (distance, label) in enumerate(ranked):
            distances[0][index] = distance
            labels[0][index] = label
        return distances, labels


class FakeFaissModule:
    @staticmethod
    def IndexFlatL2(dimension):
        return object()

    @staticmethod
    def IndexIDMap2(inner):
        return FakeFaissIndex(inner)


class FakeNumpyModule:
    @staticmethod
    def asarray(values, dtype=None):
        return values

    @staticmethod
    def full(shape, fill_value, dtype=None):
        return [[fill_value for _ in range(shape[1])] for _ in range(shape[0])]


def record():
    return SearchRecord("billing-42", "Refund the duplicate charge.",
                        (0.9, 0.2), {"product": "billing"}, "demo-v1")


class LocalBackendContractTests(unittest.TestCase):
    def test_contract_rejects_mismatched_dimensions(self):
        with self.assertRaisesRegex(ValueError, "dimension"):
            validate_record(record(), 3)

    def test_faiss_post_filter_returns_stable_application_id(self):
        with patch.dict(sys.modules, {"faiss": FakeFaissModule, "numpy": FakeNumpyModule}):
            adapter = FaissAdapter(2)
            adapter.upsert(record())
            adapter.upsert(SearchRecord(
                "shipping-8", "Track a parcel.", (0.95, 0.1),
                {"product": "shipping"}, "demo-v1",
            ))

            hits = adapter.search((1.0, 0.0), filters={"product": "billing"})

        self.assertEqual([hit.record_id for hit in hits], ["billing-42"])


class ArticleDataContractTests(unittest.TestCase):
    def test_vector_file_has_one_json_object_per_line(self):
        import json
        from article_data import VECTOR_FILE
        self.assertEqual(VECTOR_FILE.suffix, ".jsonl")
        lines = VECTOR_FILE.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 5)
        for line in lines:
            article = json.loads(line)
            self.assertIsInstance(article, dict)
            self.assertEqual(set(article), {"id", "name", "product", "embedding"})

    def test_invalid_jsonl_records_report_the_line_number(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        from article_data import load_records
        with TemporaryDirectory() as directory:
            vector_file = Path(directory) / "article_vectors.jsonl"
            for content, message in [("{bad}\n", "invalid JSON"), ("[]\n", "expected an article object")]:
                with self.subTest(content=content):
                    vector_file.write_text(content, encoding="utf-8")
                    with patch("article_data.VECTOR_FILE", vector_file):
                        with self.assertRaisesRegex(ValueError, "article_vectors.jsonl:1: " + message):
                            load_records()

    def test_jsonl_order_and_names_are_independent_of_markdown_body(self):
        from article_data import load_records, ARTICLES_DIR
        expected = ["Reset your password", "Charged twice for the same purchase",
                    "Change your payment method", "Check a refund", "Find a delayed parcel"]
        records = load_records()
        self.assertEqual([record.name for record in records], expected)
        for item in records:
            self.assertIn(item.record_id, ["account-73", "billing-42", "billing-68", "billing-25", "shipping-91"])
            self.assertEqual(item.document, (ARTICLES_DIR / f"{item.record_id}.md").read_text().strip())
            self.assertFalse(item.document.startswith("#"))
            self.assertNotEqual(item.name, item.document.splitlines()[0])

    def test_duckdb_and_faiss_use_explicit_names_and_billing_filter(self):
        from article_data import load_records
        from demo_duckdb import search_with_duckdb
        from demo_faiss import search_with_faiss
        expected = ["Charged twice for the same purchase", "Check a refund", "Change your payment method"]
        records = load_records()
        for search in (search_with_duckdb, search_with_faiss):
            with self.subTest(backend=search.__name__):
                result = search(records)
                self.assertEqual([name for _, name, _ in result], expected)
                self.assertEqual([id for id, _, _ in result], ["billing-42", "billing-25", "billing-68"])
                for actual, distance in zip(result, ([0.0, 0.1, 0.2] if search == search_with_duckdb else [0.0, 0.2, 0.4])):
                    self.assertAlmostEqual(actual[2], distance, places=5)


if __name__ == "__main__":
    unittest.main()
