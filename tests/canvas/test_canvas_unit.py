from pathlib import Path

import unittest
from shapely.geometry import Polygon

from mapengraver.canvas import CanvasBuilder, Canvas
from mapengraver.canvas.canvas_unit import CanvasUnit
from mapengraver.graphicshelper import CairoHelper


class TestCanvasUnit(unittest.TestCase):
    """
    Each output format should have a square in the top left corner. This tests
    that the scale is correct, both from the perspective of the canvas (The
    canvas dimensions should match the units), and the polygons drawn (The
    midpoint of the canvas).
    """
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_comparisons(self):
        assert CanvasUnit.from_in(1).pt > CanvasUnit.from_cm(1).pt
        assert CanvasUnit.from_cm(1).pt > CanvasUnit.from_mm(1).pt
        assert CanvasUnit.from_mm(1).pt > CanvasUnit.from_pt(1).pt

    def test_identity(self):
        assert CanvasUnit.from_pt(1).pt == 1
        assert CanvasUnit.from_in(1).inches == 1
        assert CanvasUnit.from_cm(1).cm == 1
        assert CanvasUnit.from_mm(1).mm == 1
        assert CanvasUnit.from_px(1).px == 1

        assert CanvasUnit.from_pt(2).pt == 2
        assert CanvasUnit.from_in(2).inches == 2
        assert CanvasUnit.from_cm(2).cm == 2
        assert CanvasUnit.from_mm(2).mm == 2
        assert CanvasUnit.from_px(2).px == 2

    def test_outputs(self):
        surface_types = [
            ('pdf', 1), ('svg', 1), ('png', 0.5), ('png', 1), ('png', 2)
        ]
        units = ['pt', 'in', 'cm', 'mm', 'px']

        for (surface_type, pixel_scale_factor) in surface_types:
            for unit in units:
                path = Path(__file__).parent\
                    .joinpath('output/canvas_unit_%s_%s_x%s.%s' % (surface_type, unit, pixel_scale_factor, surface_type))
                path.unlink(missing_ok=True)
                canvas_builder = CanvasBuilder()
                canvas_builder.set_path(path)
                canvas_builder.set_size(100, 100, unit)
                canvas_builder.set_pixel_scale_factor(pixel_scale_factor)

                canvas = canvas_builder.build()
                self.draw_rectangle_top_left(canvas, unit)
                canvas.close()

                assert path.exists()

    @staticmethod
    def draw_rectangle_top_left(canvas: Canvas, units: str):
        midpoint = CanvasUnit.from_unit(50, units).pt
        top_left = (0, 0)
        top_right = (midpoint, 0)
        bottom_left = (0, midpoint)
        bottom_right = (midpoint, midpoint)

        shape = Polygon([
            top_left,
            top_right,
            bottom_right,
            bottom_left,
            top_left
        ])

        canvas.context.set_source_rgb(0, 0, 0)
        CairoHelper.draw_polygon(canvas.context, shape)
        canvas.context.fill()

        point_unit_shape = Polygon([
            (0, 0),
            (0, 1),
            (1, 1),
            (1, 0),
            (0, 0)
        ])

        canvas.context.set_source_rgb(1, 0, 0)
        CairoHelper.draw_polygon(canvas.context, point_unit_shape)
        canvas.context.fill()
