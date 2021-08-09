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
