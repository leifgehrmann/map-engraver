import math

from pathlib import Path

import unittest
from unittest.mock import MagicMock
from shapely.geometry import Polygon, MultiPolygon

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.drawable.geometry.stripe_stroked_polygon_drawer import \
    StripeStrokedPolygonDrawer


class TestStripeStrokedPolygonDrawer(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_validation(self):
        with self.assertRaisesRegex(
                Exception,
                'length of stripe_widths is not the same as stripe_colors'
        ):
            drawer = StripeStrokedPolygonDrawer()
            drawer.stripe_colors = [(0, 1, 0), None]
            drawer.stripe_widths = [Cu.from_pt(10)]
            drawer.stripe_stroke_widths = [Cu.from_pt(1)]
            drawer.draw(MagicMock())

        with self.assertRaisesRegex(
                Exception,
                'length of stripe_widths is not the same as '
                'stripe_stroke_widths'
        ):
            drawer = StripeStrokedPolygonDrawer()
            drawer.stripe_colors = [(0, 1, 0), (0, 1, 0)]
            drawer.stripe_widths = [Cu.from_pt(10), Cu.from_pt(20)]
            drawer.stripe_stroke_widths = [Cu.from_pt(1)]
            drawer.draw(MagicMock())

        with self.assertRaisesRegex(
                Exception,
                'stripe_widths must contain at least one value'
        ):
            drawer = StripeStrokedPolygonDrawer()
            drawer.stripe_colors = []
            drawer.stripe_widths = []
            drawer.stripe_stroke_widths = []
            drawer.draw(MagicMock())

        with self.assertRaisesRegex(
                Exception,
                'stripe_widths must be a positive non-zero length'
        ):
            drawer = StripeStrokedPolygonDrawer()
            drawer.stripe_colors = [(0, 1, 0), (0, 1, 0)]
            drawer.stripe_widths = [Cu.from_pt(10), Cu.from_pt(0)]
            drawer.stripe_stroke_widths = [Cu.from_pt(1), Cu.from_pt(2)]
            drawer.draw(MagicMock())

        with self.assertRaisesRegex(
                Exception,
                'stripe_stroke_widths must be a positive non-zero length'
        ):
            drawer = StripeStrokedPolygonDrawer()
            drawer.stripe_colors = [(0, 1, 0), (0, 1, 0)]
            drawer.stripe_widths = [Cu.from_pt(10), Cu.from_pt(10)]
            drawer.stripe_stroke_widths = [Cu.from_pt(-1), Cu.from_pt(0)]
            drawer.draw(MagicMock())

    def test_single_stripe(self):
        path = Path(__file__).parent.joinpath(
            'output/stripe_stroked_polygon_drawer_single.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        drawer = StripeStrokedPolygonDrawer()
        drawer.stripe_colors = [(0, 1, 0)]
        drawer.stripe_widths = [Cu.from_pt(10)]
        drawer.stripe_stroke_widths = [Cu.from_pt(1)]
        drawer.geoms = [
            Polygon([
                (30, 30),
                (70, 30),
                (70, 70),
                (30, 70),
                (30, 30),
            ])
        ]
        drawer.draw(canvas)

        drawer.geoms = [
            Polygon([
                (40, 40),
                (60, 40),
                (60, 60),
                (40, 60),
                (40, 40),
            ])
        ]
        drawer.stripe_colors = [None]
        drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert data.find('M 30 30 L 70 30') != -1
            assert data.find('M 70 70 L 30 70') != -1
            assert data.find('M 30 40 L 70 40') != -1
            assert data.find('M 30 50 L 70 50') != -1
            assert data.find('M 30 60 L 70 60') != -1
            assert data.count('stroke:rgb(0%,100%,0%)') == 5
            assert data.count('stroke-width:1') == 5

    def test_two_vertical_stripes(self):
        path = Path(__file__).parent.joinpath(
            'output/stripe_stroked_polygon_drawer_two_vertical_stripes.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        drawer = StripeStrokedPolygonDrawer()
        drawer.stripe_colors = [(0, 1, 0), (0, 0, 1)]
        drawer.stripe_widths = [Cu.from_pt(20), Cu.from_pt(20)]
        drawer.stripe_stroke_widths = [Cu.from_pt(1), Cu.from_pt(2)]
        drawer.stripe_origin = CanvasCoordinate.from_pt(30, 30)
        drawer.stripe_angle = math.pi / 2  # Vertical stripes
        drawer.geoms = [
            Polygon([
                (30, 30),
                (70, 30),
                (70, 70),
                (30, 70),
                (30, 30),
            ])
        ]
        drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert data.find('M 30 70 L 30 30') != -1
            assert data.find('M 50 30 L 50 70') != -1
            assert data.find('stroke:rgb(0%,100%,0%)') != -1
            assert data.find('stroke:rgb(0%,0%,100%)') != -1
            assert data.find('stroke-width:1') != -1
            assert data.find('stroke-width:2') != -1

    def test_large_stripes(self):
        path = Path(__file__).parent.joinpath(
            'output/stripe_stroked_polygon_drawer_large_stripes.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        drawer = StripeStrokedPolygonDrawer()
        drawer.stripe_colors = [(0, 1, 0), (0, 0, 1)]
        drawer.stripe_widths = [Cu.from_pt(7), Cu.from_pt(7)]
        drawer.stripe_stroke_widths = [Cu.from_pt(1), Cu.from_pt(2)]
        drawer.stripe_origin = CanvasCoordinate.from_pt(30, 30)
        drawer.stripe_angle = -math.pi / 2  # Vertical stripes
        drawer.geoms = [
            Polygon([
                (30, 30),
                (70, 30),
                (70, 70),
                (30, 70),
                (30, 30),
            ])
        ]
        drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert data.find('M 44 70 L 44 30') != -1
            assert data.find('M 58 70 L 58 30') != -1
            assert data.find('M 37 70 L 37 30') != -1
            assert data.find('M 51 70 L 51 30') != -1
            assert data.find('M 65 70 L 65 30') != -1
            assert data.find('stroke:rgb(0%,100%,0%)') != -1
            assert data.find('stroke:rgb(0%,0%,100%)') != -1
            assert data.find('stroke:rgb(0%,100%,0%)') < \
                   data.find('stroke:rgb(0%,0%,100%)')

    def test_multi_polygons(self):
        path = Path(__file__).parent.joinpath(
            'output/stripe_stroked_polygon_drawer_multi_polygons.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        drawer = StripeStrokedPolygonDrawer()
        drawer.stripe_colors = [(1, 1, 0), None, (0.7, 0, 0.7), (0, 0, 0)]
        drawer.stripe_widths = [
            Cu.from_pt(5), Cu.from_pt(5), Cu.from_pt(5), Cu.from_pt(5),
        ]
        drawer.stripe_stroke_widths = [
            Cu.from_pt(1), None, Cu.from_pt(3), Cu.from_pt(4)
        ]
        drawer.stripe_origin = CanvasCoordinate.from_pt(30, 30)
        drawer.stripe_angle = math.pi / 8  # Vertical stripes
        drawer.geoms = [
            MultiPolygon([
                Polygon([
                    (30, 30),
                    (70, 30),
                    (70, 70),
                    (30, 70),
                    (30, 30),
                ], [[
                    (35, 35),
                    (65, 35),
                    (65, 65),
                    (35, 65),
                    (35, 35),
                ]]),
                Polygon([
                    (40, 40),
                    (60, 40),
                    (60, 60),
                    (40, 60),
                    (40, 40),
                ])
            ])
        ]
        drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert data.count('stroke:rgb(100%,100%,0%)') == 6
            assert data.count('stroke:rgb(0%,0%,0%)') == 6
            assert data.count('stroke:rgb(70%,0%,70%)') == 6
            assert data.count('stroke-width:1') == 6
            assert data.count('stroke-width:3') == 6
            assert data.count('stroke-width:4') == 6
