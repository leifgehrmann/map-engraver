from pangocffi import Alignment
from pathlib import Path

import unittest

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.data.pango.layout import Layout


class TestLayout(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_setters_and_getters(self):
        # Create a canvas for the sake of instantiating a layout object. We do
        # this because that is how Pango actually resolves the font dimensions.
        path = Path(__file__).parent.joinpath(
            'output/layout_setters_and_getters.svg'
        )
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))
        canvas = canvas_builder.build()

        layout = Layout(canvas)
        layout.set_text('Hello world')
        layout.set_markup('<span weight="bold">Hello world!</span>')

        assert layout.width is None
        assert layout.height is None
        layout.width = Cu.from_pt(100)
        layout.height = Cu.from_pt(50)
        assert layout.width.pt == 100
        assert layout.height.pt == 50
        layout.reset_width()
        layout.reset_height()
        assert layout.width is None
        assert layout.height is None

        assert layout.position.x.pt == 0
        assert layout.position.y.pt == 0
        layout.position = CanvasCoordinate(Cu.from_pt(10), Cu.from_pt(5))
        assert layout.position.x.pt == 10
        assert layout.position.y.pt == 5

        assert layout.color == (0, 0, 0, 1)
        layout.color = (0, 1, 0, 0.5)
        assert layout.color == (0, 1, 0, 0.5)

        assert layout.alignment == Alignment.LEFT
        layout.alignment = Alignment.RIGHT
        assert layout.alignment == Alignment.RIGHT

        extents = layout.logical_extents
        assert extents.pos.x.pt == 10
        assert extents.pos.y.pt == 5
        assert extents.width.pt > 1
        assert extents.height.pt > 1
