import unittest

from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate as Cc
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu


class TestCanvasBbox(unittest.TestCase):
    def test_init(self):
        bbox = CanvasBbox(Cc.from_in(1, 2), Cc.from_in(4, 6))
        assert bbox.min_pos == Cc.from_in(1, 2)
        assert bbox.max_pos == Cc.from_in(4, 6)

    def test_invalid_init(self):
        with self.assertRaises(Exception):
            CanvasBbox(Cc.from_in(4, 2), Cc.from_in(1, 6))
        with self.assertRaises(Exception):
            CanvasBbox(Cc.from_in(1, 6), Cc.from_in(4, 2))

    def test_identity(self):
        bbox = CanvasBbox.from_size(
            Cu.from_pt(1), Cu.from_pt(2), Cu.from_pt(3), Cu.from_pt(4)
        )
        assert bbox.min_pos.pt == (1, 2)
        assert bbox.max_pos.pt == (4, 6)

        bbox = CanvasBbox.from_size_pt(1, 2, 3, 4)
        assert bbox.min_pos.pt == (1, 2)
        assert bbox.max_pos.pt == (4, 6)

        bbox = CanvasBbox.from_size_px(1, 2, 3, 4)
        assert bbox.min_pos.px == (1, 2)
        assert bbox.max_pos.px == (4, 6)

        bbox = CanvasBbox.from_size_in(1, 2, 3, 4)
        assert bbox.min_pos.inches == (1, 2)
        assert bbox.max_pos.inches == (4, 6)

        bbox = CanvasBbox.from_size_mm(1, 2, 3, 4)
        # Round to solve floating point issues
        assert round(bbox.min_pos.x.mm) == 1
        assert round(bbox.min_pos.y.mm) == 2
        assert round(bbox.max_pos.x.mm) == 4
        assert round(bbox.max_pos.y.mm) == 6

        bbox = CanvasBbox.from_size_cm(1, 2, 3, 4)
        # Round to solve floating point issues
        assert round(bbox.min_pos.x.cm) == 1
        assert round(bbox.min_pos.y.cm) == 2
        assert round(bbox.max_pos.x.cm) == 4
        assert round(bbox.max_pos.y.cm) == 6

    def test_width_and_height(self):
        bbox = CanvasBbox.from_size(
            Cu.from_pt(1), Cu.from_pt(2), Cu.from_pt(3), Cu.from_pt(4)
        )
        assert bbox.width.pt == 3
        assert bbox.height.pt == 4

    def test_bounds(self):
        assert CanvasBbox.from_size_pt(1, 2, 3, 4).bounds == (
            Cu.from_pt(1),
            Cu.from_pt(2),
            Cu.from_pt(4),
            Cu.from_pt(6)
        )
        assert CanvasBbox.from_size_in(1, 2, 3, 4).bounds == (
            Cu.from_in(1),
            Cu.from_in(2),
            Cu.from_in(4),
            Cu.from_in(6)
        )
