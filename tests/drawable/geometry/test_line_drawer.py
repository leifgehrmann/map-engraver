import cairocffi.constants
from pathlib import Path

import unittest
from shapely.geometry import LineString, MultiLineString

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.drawable.geometry.line_drawer import LineDrawer
from tests.utils import svg_has_style_attr


class TestLineDrawer(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_line_string(self):
        path = Path(__file__).parent.joinpath(
            'output/line_drawer_line_string.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        line_drawer = LineDrawer()
        line_drawer.stroke_color = (0, 1, 0)
        line_drawer.stroke_width = Cu.from_pt(1.5)
        line_drawer.stroke_dashes = (
            [Cu.from_pt(1), Cu.from_pt(3), Cu.from_pt(3), Cu.from_pt(3)],
            Cu.from_pt(4)
        )
        line_drawer.stroke_line_cap = cairocffi.constants.LINE_CAP_ROUND
        line_drawer.stroke_line_join = cairocffi.constants.LINE_JOIN_MITER
        line_drawer.geoms = [
            LineString([
                (30, 30),
                (70, 30),
                (70, 70),
                (30, 70),
            ])
        ]
        line_drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert svg_has_style_attr(
                data, 'path', 'd', 'M 30 30 L 70 30 L 70 70 L 30 70'
            )
            assert svg_has_style_attr(data, 'path', 'fill', 'none')
            assert svg_has_style_attr(data, 'path', 'fill', 'none')
            assert svg_has_style_attr(data, 'path', 'stroke-width', '1.5')
            assert svg_has_style_attr(
                data, 'path', 'stroke', 'rgb\\(0%, ?100%, ?0%\\)', escape=False
            )

    def test_multi_line_string(self):
        path = Path(__file__).parent.joinpath(
            'output/line_drawer_multi_line_string.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        line_drawer = LineDrawer()
        line_drawer.stroke_color = (1, 0, 0)
        line_drawer.stroke_width = Cu.from_pt(1.5)
        line_drawer.geoms = [
            MultiLineString([[
                (30, 30),
                (70, 30),
                (70, 70),
                (30, 70),
            ], [
                (40, 40),
                (40, 60),
                (60, 60),
                (60, 40),
            ]])
        ]
        line_drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert svg_has_style_attr(
                data, 'path', 'd', 'M 30 30 L 70 30 L 70 70 L 30 70'
            )
            assert svg_has_style_attr(
                data, 'path', 'd', 'M 40 40 L 40 60 L 60 60 L 60 40'
            )
            assert svg_has_style_attr(data, 'path', 'fill', 'none')
            assert svg_has_style_attr(data, 'path', 'stroke-width', '1.5')
            assert svg_has_style_attr(
                data, 'path', 'stroke', 'rgb\\(100%, ?0%, ?0%\\)', escape=False
            )
