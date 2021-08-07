from pathlib import Path

import unittest

from map_engraver.canvas.canvas_unit import CanvasUnit


class TestCanvasUnit(unittest.TestCase):
    def test_comparisons(self):
        assert CanvasUnit.from_in(1).pt > CanvasUnit.from_cm(1).pt
        assert CanvasUnit.from_cm(1).pt > CanvasUnit.from_mm(1).pt
        assert CanvasUnit.from_mm(1).pt > CanvasUnit.from_pt(1).pt

    def test_identity(self):
        assert CanvasUnit.from_pt(1).pt == 1
        assert CanvasUnit.from_in(1).inches == 1
        assert CanvasUnit.from_cm(1).cm == 1
        assert CanvasUnit.from_mm(1).mm == 1
        assert CanvasUnit.from_px(1).px == 1

        assert CanvasUnit.from_pt(2).pt == 2
        assert CanvasUnit.from_in(2).inches == 2
        assert CanvasUnit.from_cm(2).cm == 2
        assert CanvasUnit.from_mm(2).mm == 2
        assert CanvasUnit.from_px(2).px == 2

    def test_unknown_unit(self):
        with self.assertRaises(Exception):
            CanvasUnit.from_unit(1, 'unknown')
