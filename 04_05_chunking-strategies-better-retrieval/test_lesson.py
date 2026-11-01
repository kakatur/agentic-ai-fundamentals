import unittest

from chunking import chunk_text


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


if __name__ == "__main__":
    unittest.main()
