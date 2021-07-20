from typing import Tuple, Optional

import subprocess

from pathlib import Path

import unittest
from shapely.geometry import Polygon

from mapengraver.canvas import CanvasBuilder, Canvas
from mapengraver.canvas.canvas_unit import CanvasUnit
from tests.canvas.unit_scale import UnitScale
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

    def test_unknown_unit(self):
        with self.assertRaises(Exception):
            CanvasUnit.from_unit(1, 'unknown')

    def test_outputs(self):
        surface_types = [
            ('pdf', 1), ('svg', 1), ('png', 0.5), ('png', 1), ('png', 2)
        ]
        units = ['pt', 'in', 'cm', 'mm', 'px']

        for (surface_type, pixel_scale_factor) in surface_types:
            for unit in units:
                canvas_builder = CanvasBuilder()

                # We want to test all units, but some sizes are just too big
                # and will take up lots of disk space. So we make an exception
                # for inches and centimeters.
                expected_size_in_unit: int
                expected_size: Optional[CanvasUnit]
                if unit in ['in', 'cm']:
                    expected_size_in_unit = 4
                    expected_size = CanvasUnit.from_unit(4, unit)
                    # Setting to a smaller size to avoid disk space issues
                    canvas_builder.set_size(expected_size, expected_size)
                else:
                    expected_size_in_unit = 100
                    expected_size = CanvasUnit.from_unit(100, unit)
                    canvas_builder.set_size(expected_size, expected_size)

                path = Path(__file__).parent \
                    .joinpath(
                    'output/canvas_unit_%s_%f%s_x%s.%s' %
                    (
                        surface_type,
                        expected_size_in_unit,
                        unit,
                        pixel_scale_factor,
                        surface_type
                    )
                )
                path.unlink(missing_ok=True)
                canvas_builder.set_path(path)
                canvas_builder.set_pixel_scale_factor(pixel_scale_factor)

                canvas = canvas_builder.build()
                self.draw_rectangle_top_left(canvas, unit)
                canvas.close()

                assert path.exists()

                actual_size = self.get_file_dimensions_using_imagemagick(path)
                if surface_type == 'pdf':
                    self.assert_match(
                        expected_size_in_unit, unit, surface_type,
                        1, actual_size, expected_size.pt
                    )
                elif surface_type == 'svg':
                    self.assert_match(
                        expected_size_in_unit, unit, surface_type,
                        1, actual_size, expected_size.px
                    )
                elif surface_type == 'png':
                    self.assert_match(
                        expected_size_in_unit, unit, surface_type,
                        pixel_scale_factor, actual_size, expected_size.px
                    )

    @staticmethod
    def draw_rectangle_top_left(canvas: Canvas, unit: str):
        if unit in ['in', 'cm']:
            # Setting to a smaller size to avoid disk space issues
            midpoint = CanvasUnit.from_unit(2, unit).pt
        else:
            midpoint = CanvasUnit.from_unit(50, unit).pt
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

    @staticmethod
    def get_file_dimensions_using_imagemagick(
            path: Path
    ) -> Tuple[float, float]:
        pipe = subprocess.Popen(
            ['identify', '-format', "%P", path.as_posix()],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        stdout, stderr = pipe.communicate()
        w, h = str(stdout.decode('utf-8')).split('\n')[0].split('x')
        return float(w), float(h)

    @staticmethod
    def assert_match(
            expected_size_in_unit,
            unit,
            surface_type,
            pixel_scale_factor,
            actual,
            expected
    ):
        if round(actual[0]/pixel_scale_factor) != round(expected):
            raise AssertionError(
                'mismatched-size for %s%s.%s x%d. expected: %f, actual: %f' % (
                    expected_size_in_unit,
                    unit,
                    surface_type,
                    pixel_scale_factor,
                    actual[0],
                    expected
                )
            )
        if round(actual[1]/pixel_scale_factor) != round(expected):
            raise AssertionError(
                'mismatched-size for %s%s.%s x%d. expected: %f, actual: %f' % (
                    expected_size_in_unit,
                    unit,
                    surface_type,
                    pixel_scale_factor,
                    actual[1],
                    expected
                )
            )

    def test_unit_scale(self):
        surface_types = ['png', 'svg', 'pdf']
        for surface_type in surface_types:
            path = Path(__file__).parent\
                .joinpath('output/canvas_unit_unit_scale.%s' % surface_type)
            path.unlink(missing_ok=True)
            canvas_builder = CanvasBuilder()
            canvas_builder.set_path(path)
            canvas_builder.set_size(
                CanvasUnit.from_in(1),
                CanvasUnit.from_in(1)
            )

            canvas = canvas_builder.build()

            UnitScale().draw(canvas)

            canvas.close()

            assert path.exists()
