from pathlib import Path

import unittest

from mapengraver.canvas.canvas_unit import CanvasUnit


class TestCanvasUnit(unittest.TestCase):
    """
    Each output format should have a square in the top left corner. This tests
    that the scale is correct, both from the perspective of the canvas (The
    canvas dimensions should match the units), and the polygons drawn (The
    midpoint of the canvas).
    """
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

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
