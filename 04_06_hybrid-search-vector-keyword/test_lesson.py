import unittest
from hybrid import DIMENSIONS, build, connect, fuse, search


def vector(index):
    v = [0.0] * DIMENSIONS
    v[index] = 1.0
    return v


class HybridTests(unittest.TestCase):
    def test_fusion_and_duplicates(self):
        result = fuse([["a", "a", "b"], ["b", "a"]], k=0)
        self.assertEqual([x[0] for x in result], ["a", "b"])
        self.assertAlmostEqual(result[0][1], 1.5)

    def test_search_filters_and_model(self):
        con = connect(":memory:")
        build(con, [("a", "public", "E104 recovery"), ("b", "private", "E104 recovery")], [vector(0), vector(0)])
        dense, lexical, fused = search(con, "E104", vector(0), "public")
        for ranking in (dense, lexical, fused):
            self.assertEqual([x[0] for x in ranking], ["a"])
        self.assertEqual(search(con, "E104", vector(0), "missing"), ([], [], []))
        with self.assertRaises(ValueError):
            search(con, "E104", vector(0), "public", model="different")
        con.close()

    def test_invalid_input(self):
        con = connect(":memory:")
        with self.assertRaises(ValueError):
            build(con, [("a", "x", "text")], [])
        with self.assertRaises(ValueError):
            search(con, " ", vector(0), "x")
        con.close()


if __name__ == "__main__":
    unittest.main()
