import unittest
from chunking import window_chunks, section_chunks, expand_parent
class ChunkTests(unittest.TestCase):
    def test_overlap_preserves_boundary_words(self):
        chunks=window_chunks("one two three four five six",4,2); self.assertEqual(chunks[0].text.split()[-2:],chunks[1].text.split()[:2])
    def test_offsets_are_stable(self):
        self.assertEqual((window_chunks("a b c",2)[1].start,window_chunks("a b c",2)[1].end),(2,3))
    def test_invalid_overlap_fails(self):
        with self.assertRaises(ValueError): window_chunks("a b",2,2)
if __name__ == "__main__": unittest.main()
