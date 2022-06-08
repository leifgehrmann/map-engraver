from pathlib import Path

import unittest
from shapely.geometry import Polygon, MultiPolygon

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.drawable.geometry.stripe_filled_polygon_drawer import \
    StripeFilledPolygonDrawer


class TestPolygonDrawer(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

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
