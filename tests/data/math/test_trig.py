import unittest

from map_engraver.data.math.trig import obtuse_angle


class TestTrig(unittest.TestCase):
    def test_obtuse_angle(self):
        # If either `a` or `b` have the same coordinate as `c`, return `inf`.
        self.assertEqual(obtuse_angle((1, 0), (0, 0), (0, 0)), float('inf'))
        self.assertEqual(obtuse_angle((0, 0), (1, 0), (0, 0)), float('inf'))
        self.assertEqual(obtuse_angle((0, 0), (0, 0), (0, 0)), float('inf'))

        # Go round in a unit circle, with `a` remaining as `(1, 0)`.
        self.assertEqual(obtuse_angle((1, 0), (1, 0), (0, 0)), 0)
        self.assertAlmostEqual(obtuse_angle((1, 0), (1, 1), (0, 0)), 45, 10)
        self.assertEqual(obtuse_angle((1, 0), (0, 1), (0, 0)), 90)
        self.assertAlmostEqual(obtuse_angle((1, 0), (-1, 1), (0, 0)), 135, 10)
        self.assertEqual(obtuse_angle((1, 0), (-1, 0), (0, 0)), 180)
        self.assertAlmostEqual(obtuse_angle((1, 0), (-1, -1), (0, 0)), 135, 10)
        self.assertEqual(obtuse_angle((1, 0), (0, -1), (0, 0)), 90)
        self.assertAlmostEqual(obtuse_angle((1, 0), (1, -1), (0, 0)), 45, 10)
