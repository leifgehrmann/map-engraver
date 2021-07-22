from pathlib import Path

import unittest

from mapengraver.canvas import CanvasBuilder
from mapengraver.canvas.canvas_unit import CanvasUnit as Cu
from mapengraver.drawable.geometry.polygon_drawer import PolygonDrawer


class TestPolygonDrawer(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_outputs_color(self):
        path = Path(__file__).parent.joinpath('output/background.svg')
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_px(100), Cu.from_px(100))

        canvas = canvas_builder.build()

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (1, 0, 0)
        polygon_drawer.stroke_color = (0, 1, 0)
        polygon_drawer.stroke_width = Cu.from_pt(2)
        polygon_drawer.polygons =
        polygon_drawer.draw(canvas)

        canvas.close()

        assert path.exists()
