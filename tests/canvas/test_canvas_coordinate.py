from pathlib import Path

import unittest

from map_engraver.canvas.canvas_coordinate import CanvasCoordinate as Cc


class TestCanvasCoordinate(unittest.TestCase):
    def test_comparisons(self):
        assert Cc.from_in(1, 1).pt[0] > Cc.from_cm(1, 1).pt[0]
        assert Cc.from_cm(1, 1).pt[0] > Cc.from_mm(1, 1).pt[0]
        assert Cc.from_mm(1, 1).pt[0] > Cc.from_pt(1, 1).pt[0]

    def test_identity(self):
        assert Cc.from_pt(1, 1).pt == (1, 1)
        assert Cc.from_in(1, 1).inches == (1, 1)
        assert Cc.from_cm(1, 1).cm == (1, 1)
        assert Cc.from_mm(1, 1).mm == (1, 1)
        assert Cc.from_px(1, 1).px == (1, 1)

        assert Cc.from_pt(2, 2).pt == (2, 2)
        assert Cc.from_in(2, 2).inches == (2, 2)
        assert Cc.from_cm(2, 2).cm == (2, 2)
        assert Cc.from_mm(2, 2).mm == (2, 2)
        assert Cc.from_px(2, 2).px == (2, 2)
