import unittest

from chunking import Chunk, expand_parent, section_chunks, window_chunks


class ChunkTests(unittest.TestCase):
    def test_overlap_repeats_boundary_words(self):
        chunks = window_chunks("one two three four five six", 4, 2)
        self.assertEqual(chunks[0].text.split()[-2:], chunks[1].text.split()[:2])

    def test_offsets_are_stable(self):
        self.assertEqual((window_chunks("a b c", 2)[1].start_word, window_chunks("a b c", 2)[1].end_word), (2, 3))

    def test_sections_preserve_heading_and_parent(self):
        chunk = section_chunks([("Reset", "Open settings")], "guide")[0]
        self.assertEqual(chunk.text, "Reset Open settings")
        self.assertEqual(expand_parent(chunk, {"guide": "full guide"}), "full guide")

    def test_invalid_overlap_fails(self):
        with self.assertRaises(ValueError):
            window_chunks("a b", 2, 2)


if __name__ == "__main__":
    unittest.main()
