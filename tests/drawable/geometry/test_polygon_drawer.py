from pathlib import Path

import unittest
from shapely.geometry import Polygon, MultiPolygon

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer


class TestPolygonDrawer(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_only_fill(self):
        path = Path(__file__).parent.joinpath(
            'output/polygon_drawer_only_fill.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0, 1, 0)
        polygon_drawer.geoms = [
            Polygon([
                (30, 30),
                (70, 30),
                (70, 70),
                (30, 70),
                (30, 30),
            ])
        ]
        polygon_drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert data.find('M 30 30 L 70 30 L 70 70 L 30 70 Z M 30 30') != -1
            assert data.find('fill:rgb(0%,100%,0%)') != -1
            assert data.find('stroke:none') != -1
            assert data.find('stroke-width:') == -1

    def test_only_stroke(self):
        path = Path(__file__).parent.joinpath(
            'output/polygon_drawer_only_stroke.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        polygon_drawer = PolygonDrawer()
        polygon_drawer.stroke_color = (0, 1, 0)
        polygon_drawer.stroke_width = Cu.from_pt(1.5)
        polygon_drawer.geoms = [
            Polygon([
                (30, 30),
                (70, 30),
                (70, 70),
                (30, 70),
                (30, 30),
            ])
        ]
        polygon_drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert data.find('M 30 30 L 70 30 L 70 70 L 30 70 Z M 30 30') != -1
            assert data.find('fill:none') != -1
            assert data.find('stroke-width:1.5') != -1
            assert data.find('stroke:rgb(0%,100%,0%);') != -1

    def test_fill_preserve(self):
        path = Path(__file__).parent.joinpath(
            'output/polygon_drawer_fill_preserve.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (1, 0, 0)
        polygon_drawer.stroke_color = (0, 1, 0)
        polygon_drawer.stroke_width = Cu.from_pt(2)
        polygon_drawer.geoms = [
            Polygon([
                (30, 30),
                (70, 30),
                (70, 70),
                (30, 70),
                (30, 30),
            ])
        ]
        polygon_drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert data.find('M 30 30 L 70 30 L 70 70 L 30 70 Z M 30 30') != -1
            assert data.find('fill:rgb(100%,0%,0%)') != -1
            assert data.find('stroke-width:2') != -1
            assert data.find('stroke:rgb(0%,100%,0%);') != -1

    def test_multipolygons(self):
        path = Path(__file__).parent.joinpath(
            'output/polygon_drawer_multipolygons.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        polygon_drawer = PolygonDrawer()
        polygon_drawer.stroke_color = (0, 1, 0)
        polygon_drawer.stroke_width = Cu.from_pt(1.5)
        polygon_drawer.geoms = [
            MultiPolygon([
                Polygon([
                    (30, 30),
                    (40, 30),
                    (40, 70),
                    (30, 70),
                    (30, 30),
                ]),
                Polygon([
                    (60, 30),
                    (70, 30),
                    (70, 70),
                    (60, 70),
                    (60, 30),
                ])
            ])
        ]
        polygon_drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert data.find('M 30 30 L 40 30 L 40 70 L 30 70 Z M 30 30') != -1
            assert data.find('M 60 30 L 70 30 L 70 70 L 60 70 Z M 60 30') != -1
            assert data.find('fill:none') != -1
            assert data.find('stroke-width:1.5') != -1
            assert data.find('stroke:rgb(0%,100%,0%);') != -1
