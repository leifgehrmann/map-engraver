import unittest
from shapely.geometry import Point

from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data.canvas_geometry.rect import rounded_rect


class TestRect(unittest.TestCase):
    def test_exception_is_thrown_with_invalid_sizes(self):
        with self.assertRaises(Exception):
            rounded_rect(
                CanvasBbox.from_px(10, 20, 0, 40),
                CanvasUnit.from_px(10)
            )
        with self.assertRaises(Exception):
            rounded_rect(
                CanvasBbox.from_px(10, 20, 30, 0),
                CanvasUnit.from_px(10)
            )
        with self.assertRaises(Exception):
            rounded_rect(
                CanvasBbox.from_px(10, 20, 30, 40),
                CanvasUnit.from_px(-10)
            )

    def test_rounded_rect_without_radius_is_returned(self):
        rr = rounded_rect(
            CanvasBbox.from_pt(10, 20, 30, 40),
            CanvasUnit.from_pt(0)
        )
        assert rr.bounds == (10, 20, 40, 60)
        assert rr.touches(Point(*CanvasCoordinate.from_pt(10, 20).pt))
        assert rr.contains(Point(*CanvasCoordinate.from_pt(15, 25).pt))

    def test_rounded_rect_with_radius_is_returned(self):
        rr = rounded_rect(
            CanvasBbox.from_pt(10, 20, 30, 40),
            CanvasUnit.from_pt(5)
        )
        assert rr.bounds == (10, 20, 40, 60)
        assert not rr.contains(Point(*CanvasCoordinate.from_pt(10, 20).pt))
        assert rr.contains(Point(*CanvasCoordinate.from_pt(15, 25).pt))
