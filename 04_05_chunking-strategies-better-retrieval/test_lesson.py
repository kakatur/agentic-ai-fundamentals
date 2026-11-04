import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

import demo

from chunking import chunk_text
from demo import BODY, HEADING, paragraph_chunk


class ChunkingTests(unittest.TestCase):
    def test_overlap_preserves_source_offsets_and_repeated_words(self):
        chunks = chunk_text("A B C D E F", source_id="doc-v1", chunk_size=4, overlap=2)
        self.assertEqual([(chunk.start_word, chunk.end_word) for chunk in chunks], [(0, 4), (2, 6)])
        self.assertEqual(chunks[0].chunk_id, "doc-v1:0-4")
        self.assertEqual(chunks[1].text, "C D E F")

    def test_empty_text_has_no_chunks(self):
        self.assertEqual(chunk_text("", source_id="doc", chunk_size=4), [])

    def test_invalid_overlap_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            chunk_text("A B C", source_id="doc", chunk_size=2, overlap=2)

    def test_source_id_is_required(self):
        with self.assertRaisesRegex(ValueError, "source_id"):
            chunk_text("A B", source_id=" ", chunk_size=2)

    def test_heading_is_metadata_and_not_part_of_searchable_text(self):
        chunk = paragraph_chunk(BODY, source_id="refund-procedure-001")[0]
        self.assertEqual(chunk.text, BODY)
        self.assertNotIn(HEADING, chunk.text)
        self.assertEqual(chunk.metadata["section_heading"], HEADING)
        self.assertEqual(chunk.metadata["document_title"], HEADING)
        self.assertEqual(chunk.metadata["document_id"], "refund-procedure-001")
        self.assertEqual(chunk.metadata["chunk_index"], 1)

    def test_eight_word_windows_split_body_into_three_chunks(self):
        chunks = chunk_text(
            BODY,
            source_id="refund-procedure-001",
            chunk_size=8,
            metadata={"section_heading": HEADING},
        )
        self.assertEqual(len(chunks), 3)
        self.assertTrue(all(HEADING not in chunk.text for chunk in chunks))
        self.assertEqual([chunk.metadata["chunk_index"] for chunk in chunks], [1, 2, 3])

    def test_three_word_overlap_creates_five_chunks(self):
        chunks = chunk_text(BODY, source_id="refund-v1", chunk_size=8, overlap=3)
        self.assertEqual(len(chunks), 5)
        self.assertEqual((chunks[1].start_word, chunks[1].end_word), (5, 13))
        self.assertEqual(chunks[1].text, "have settled. Then refund the duplicate charge and")
        self.assertEqual((chunks[-1].start_word, chunks[-1].end_word), (20, 24))

    def test_changed_query_can_rank_transaction_validation_first(self):
        output = StringIO()
        with patch.object(demo, "QUERY", "both transactions settled"), redirect_stdout(output):
            demo.main()
        sentence_results = output.getvalue().split("2) Sentence units", 1)[1].split("3)", 1)[0]
        self.assertIn("word_overlap=3  refund-procedure-001:sentence-1", sentence_results.splitlines()[1])
        self.assertNotIn("The top sentence chunk has the refund action and timing", output.getvalue())
        self.assertIn("vectors if embedded", output.getvalue())


if __name__ == "__main__":
    unittest.main()
