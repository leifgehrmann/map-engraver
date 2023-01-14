import pangocffi
import unittest

from map_engraver.canvas.canvas_unit import CanvasUnit


class TestCanvasUnit(unittest.TestCase):
    def test_comparisons(self):
        assert CanvasUnit.from_in(1).pt > CanvasUnit.from_cm(1).pt
        assert CanvasUnit.from_cm(1).pt > CanvasUnit.from_mm(1).pt
        assert CanvasUnit.from_mm(1).pt > CanvasUnit.from_pt(1).pt
        assert CanvasUnit.from_pt(1).pt > CanvasUnit.from_px(1).pt
        assert CanvasUnit.from_px(1).pt > CanvasUnit.from_pango(1).pt

    def test_identity(self):
        assert CanvasUnit.from_pt(1).pt == 1
        assert CanvasUnit.from_in(1).inches == 1
        assert CanvasUnit.from_cm(1).cm == 1
        assert CanvasUnit.from_mm(1).mm == 1
        assert CanvasUnit.from_px(1).px == 1
        assert CanvasUnit.from_pango(1).pango == 1

        assert CanvasUnit.from_pt(2).pt == 2
        assert CanvasUnit.from_in(2).inches == 2
        assert CanvasUnit.from_cm(2).cm == 2
        assert CanvasUnit.from_mm(2).mm == 2
        assert CanvasUnit.from_px(2).px == 2
        assert CanvasUnit.from_pango(2).pango == 2

    def test_pango_units_are_not_floating_point(self):
        assert CanvasUnit.from_pt(1/4096).pango == 0
        assert CanvasUnit.from_pt(2/1024 - 1/4096).pango == 2
        assert CanvasUnit.from_pt(2/1024 + 1/4096).pango == 2

    def test_pango_scale_is_consistent_with_library(self):
        assert CanvasUnit.from_pt(2).pango == pangocffi.units_from_double(2)
        assert CanvasUnit.from_pango(512).pt == pangocffi.units_to_double(512)

    def test_eq(self):
        assert CanvasUnit.from_cm(2) == CanvasUnit.from_cm(2)
        assert CanvasUnit.from_cm(2) != 2

    # noinspection PyStatementEffect
    def test_gt_ge_lt_le(self):
        assert not CanvasUnit.from_cm(3) > CanvasUnit.from_cm(5)
        assert not CanvasUnit.from_cm(5) > CanvasUnit.from_cm(5)
        assert CanvasUnit.from_cm(7) > CanvasUnit.from_cm(5)
        assert not CanvasUnit.from_cm(3) >= CanvasUnit.from_cm(5)
        assert CanvasUnit.from_cm(5) >= CanvasUnit.from_cm(5)
        assert CanvasUnit.from_cm(7) >= CanvasUnit.from_cm(5)
        assert CanvasUnit.from_cm(3) < CanvasUnit.from_cm(5)
        assert not CanvasUnit.from_cm(5) < CanvasUnit.from_cm(5)
        assert not CanvasUnit.from_cm(7) < CanvasUnit.from_cm(5)
        assert CanvasUnit.from_cm(3) <= CanvasUnit.from_cm(5)
        assert CanvasUnit.from_cm(5) <= CanvasUnit.from_cm(5)
        assert not CanvasUnit.from_cm(7) <= CanvasUnit.from_cm(5)
        with self.assertRaises(NotImplementedError):
            CanvasUnit.from_cm(1) > 1
        with self.assertRaises(NotImplementedError):
            CanvasUnit.from_cm(1) >= 1
        with self.assertRaises(NotImplementedError):
            CanvasUnit.from_cm(1) < 1
        with self.assertRaises(NotImplementedError):
            CanvasUnit.from_cm(1) <= 1

    def test_add(self):
        assert CanvasUnit.from_cm(2) + CanvasUnit.from_cm(3) == \
               CanvasUnit.from_cm(5)
        assert CanvasUnit.from_cm(2).__radd__(CanvasUnit.from_cm(3)) == \
               CanvasUnit.from_cm(5)
        assert 0 + CanvasUnit.from_cm(2) == CanvasUnit.from_cm(2)
        assert CanvasUnit.from_cm(2) + 0 == CanvasUnit.from_cm(2)
        assert sum([
            CanvasUnit.from_cm(2),
            CanvasUnit.from_cm(3),
            CanvasUnit.from_cm(4)
        ]) == CanvasUnit.from_cm(9)
        with self.assertRaises(NotImplementedError):
            CanvasUnit.from_cm(2) + 1
        with self.assertRaises(NotImplementedError):
            1 + CanvasUnit.from_cm(2)

    def test_sub(self):
        assert CanvasUnit.from_cm(2) - CanvasUnit.from_cm(3) == \
               CanvasUnit.from_cm(-1)
        with self.assertRaises(NotImplementedError):
            CanvasUnit.from_cm(2) - 1

    def test_neg(self):
        assert -CanvasUnit.from_cm(2) == CanvasUnit.from_cm(-2)

    def test_mul(self):
        assert CanvasUnit.from_cm(2.5) * 2 == CanvasUnit.from_cm(5)
        assert CanvasUnit.from_cm(2) * 2.5 == CanvasUnit.from_cm(5)

    def test_div(self):
        assert CanvasUnit.from_cm(5) / 2.5 == CanvasUnit.from_cm(2)
        assert CanvasUnit.from_cm(5) / 2 == CanvasUnit.from_cm(2.5)

    def test_unknown_unit(self):
        with self.assertRaises(Exception):
            CanvasUnit.from_unit(1, 'unknown')
