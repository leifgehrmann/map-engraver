import unittest

from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate as Cc
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu


class TestCanvasBbox(unittest.TestCase):
    def test_init(self):
        bbox = CanvasBbox(Cc.from_in(1, 2), Cu.from_in(3), Cu.from_in(4))
        assert bbox.pos == Cc.from_in(1, 2)
        assert bbox.width == Cu.from_in(3)
        assert bbox.height == Cu.from_in(4)

    def test_identity(self):
        assert CanvasBbox.from_pt(1, 2, 3, 4).pos.pt == (1, 2)
        assert CanvasBbox.from_pt(1, 2, 3, 4).width.pt == 3
        assert CanvasBbox.from_pt(1, 2, 3, 4).height.pt == 4

        assert CanvasBbox.from_px(1, 2, 3, 4).pos.px == (1, 2)
        assert CanvasBbox.from_px(1, 2, 3, 4).width.px == 3
        assert CanvasBbox.from_px(1, 2, 3, 4).height.px == 4

        assert CanvasBbox.from_in(1, 2, 3, 4).pos.inches == (1, 2)
        assert CanvasBbox.from_in(1, 2, 3, 4).width.inches == 3
        assert CanvasBbox.from_in(1, 2, 3, 4).height.inches == 4

        assert CanvasBbox.from_mm(1, 2, 3, 4).pos.mm == (1, 2)
        # Round to solve floating point issues
        assert round(CanvasBbox.from_mm(1, 2, 3, 4).width.mm) == 3
        assert CanvasBbox.from_mm(1, 2, 3, 4).height.mm == 4

        assert CanvasBbox.from_cm(1, 2, 3, 4).pos.cm == (1, 2)
        # Round to solve floating point issues
        assert round(CanvasBbox.from_cm(1, 2, 3, 4).width.cm) == 3
        assert CanvasBbox.from_cm(1, 2, 3, 4).height.cm == 4
