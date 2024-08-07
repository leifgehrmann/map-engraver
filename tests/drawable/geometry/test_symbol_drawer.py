from pathlib import Path

import unittest
from shapely.geometry import Point

from map_engraver.canvas import CanvasBuilder, Canvas
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.drawable.geometry.symbol_drawer import SymbolDrawer
from map_engraver.graphicshelper import CairoHelper
from tests.utils import svg_has_style_attr


class TestPolygonDrawer(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_z_func(self):
        path = Path(__file__).parent.joinpath(
            'output/symbol_drawer_z_func.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        class MySymbolDrawer(SymbolDrawer):
            def draw_symbol(self, key, point: Point, canvas: Canvas):
                canvas.context.set_source_rgba(point.x/100, point.y/100, 0, 1)
                CairoHelper.draw_point(
                    canvas.context,
                    point,
                    Cu.from_pt(20).pt
                )

        my_symbol_drawer = MySymbolDrawer()
        my_symbol_drawer.points = [
            Point(30, 70),
            Point(35, 60),
            Point(40, 50),
            Point(45, 40),
            Point(50, 30),
            Point(55, 40),
            Point(60, 50),
            Point(65, 60),
            Point(70, 70)
        ]
        my_symbol_drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            # Assert that the symbols appear
            assert svg_has_style_attr(
                data, 'path', 'fill', 'rgb\\(50%, ?30%, ?0%\\)', escape=False
            )
            assert svg_has_style_attr(
                data, 'path', 'fill', 'rgb\\(45%, ?40%, ?0%\\)', escape=False
            )
            assert svg_has_style_attr(
                data, 'path', 'fill', 'rgb\\(55%, ?40%, ?0%\\)', escape=False
            )
            assert data.find('rgb(50%,') < data.find('rgb(45%,')
            assert data.find('rgb(45%,') < data.find('rgb(55%,')

    def test_can_iterate_dict(self):
        path = Path(__file__).parent.joinpath(
            'output/symbol_drawer_can_iterate_dict.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        class MySymbolDrawer(SymbolDrawer):
            def draw_symbol(self, key, point: Point, canvas: Canvas):
                canvas.context.set_source_rgba(point.x/100, point.y/100, 0, 1)
                CairoHelper.draw_point(
                    canvas.context,
                    point,
                    Cu.from_pt(key).pt
                )

        my_symbol_drawer = MySymbolDrawer()
        my_symbol_drawer.points = {
            2: Point(30, 70),
            4: Point(35, 60),
            6: Point(40, 50),
            8: Point(45, 40),
            10: Point(50, 30),
            12: Point(55, 40),
            14: Point(60, 50),
            16: Point(65, 60),
            18: Point(70, 70)
        }
        my_symbol_drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            # Assert that the symbols appear with correct size
            assert svg_has_style_attr(
                data, 'path', 'd', 'M 55 30 C.*', escape=False
            )
            assert svg_has_style_attr(
                data, 'path', 'd', 'M 79 70 C.*', escape=False
            )
