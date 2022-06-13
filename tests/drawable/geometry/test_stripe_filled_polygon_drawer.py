import math

from pathlib import Path

import unittest
from unittest.mock import MagicMock
from shapely.geometry import Polygon, MultiPolygon

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.drawable.geometry.stripe_filled_polygon_drawer import \
    StripeFilledPolygonDrawer


class TestPolygonDrawer(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_validation(self):
        with self.assertRaisesRegex(
                Exception,
                'length of width_arr is not the same as color_arr'
        ):
            drawer = StripeFilledPolygonDrawer()
            drawer.stripe_colors = [(0, 1, 0), (0, 1, 0)]
            drawer.stripe_widths = [Cu.from_pt(10)]
            drawer.draw(MagicMock())

        with self.assertRaisesRegex(
                Exception,
                'width_arr must contain at least one value'
        ):
            drawer = StripeFilledPolygonDrawer()
            drawer.stripe_colors = []
            drawer.stripe_widths = []
            drawer.draw(MagicMock())

        with self.assertRaisesRegex(
                Exception,
                'width_arr must be a positive non-zero length'
        ):
            drawer = StripeFilledPolygonDrawer()
            drawer.stripe_colors = [(0, 1, 0), (0, 1, 0)]
            drawer.stripe_widths = [Cu.from_pt(10), Cu.from_pt(0)]
            drawer.draw(MagicMock())

    def test_single_stripe(self):
        path = Path(__file__).parent.joinpath(
            'output/stripe_filled_polygon_drawer_single.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        drawer = StripeFilledPolygonDrawer()
        drawer.stripe_colors = [(0, 1, 0)]
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
            assert data.find('M 30 30 L 70 30 L 70 70 L 30 70 Z M 30 30') != -1
            assert data.find('M 40 40 L 60 40 L 60 60 L 40 60 Z M 40 40') == -1
            assert data.find('fill:rgb(0%,100%,0%)') != -1
            assert data.find('stroke:none') != -1
            assert data.find('stroke-width:') == -1

    def test_two_vertical_stripes(self):
        path = Path(__file__).parent.joinpath(
            'output/stripe_filled_polygon_drawer_two_vertical_stripes.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        drawer = StripeFilledPolygonDrawer()
        drawer.stripe_colors = [(0, 1, 0), (0, 0, 1)]
        drawer.stripe_widths = [Cu.from_pt(20), Cu.from_pt(20)]
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
            assert data.find('M 30 30 L 30 70 L 50 70 L 50 30 Z M 30 30') != -1
            assert data.find('M 50 30 L 50 70 L 70 70 L 70 30 Z M 50 30') != -1
            assert data.find('fill:rgb(0%,100%,0%)') != -1
            assert data.find('fill:rgb(0%,0%,100%)') != -1
            assert data.find('stroke:none') != -1
            assert data.find('stroke-width:') == -1

    def test_large_stripes(self):
        path = Path(__file__).parent.joinpath(
            'output/stripe_filled_polygon_drawer_large_stripes.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        drawer = StripeFilledPolygonDrawer()
        drawer.stripe_colors = [(0, 1, 0), (0, 0, 1)]
        drawer.stripe_widths = [Cu.from_pt(100), Cu.from_pt(20)]
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
            assert data.find('M 30 30 L 30 70 L 70 70 L 70 30 Z M 30 30') != -1
            assert data.find('fill:rgb(0%,100%,0%)') != -1
            assert data.find('fill:rgb(0%,0%,100%)') == -1
            assert data.find('stroke:none') != -1
            assert data.find('stroke-width:') == -1

    def test_multi_polygons(self):
        path = Path(__file__).parent.joinpath(
            'output/stripe_filled_polygon_drawer_multi_polygons.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        drawer = StripeFilledPolygonDrawer()
        drawer.stripe_colors = [(1, 1, 0), None, (0.7, 0, 0.7), (0, 0, 0)]
        drawer.stripe_widths = [
            Cu.from_pt(5), Cu.from_pt(5), Cu.from_pt(5), Cu.from_pt(5),
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
            assert data.find('fill:rgb(100%,100%,0%)') != -1
            assert data.find('fill:rgb(0%,0%,0%)') != -1
            assert data.find('fill:rgb(70%,0%,70%)') != -1
            assert data.find('stroke:none') != -1
            assert data.find('stroke-width:') == -1
