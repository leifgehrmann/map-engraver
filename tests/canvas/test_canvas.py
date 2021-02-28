import unittest

from mapengraver.canvas import Canvas


class TestCanvas(unittest.TestCase):
    def test_init(self):
        Canvas('png', 123, 134, 20)
