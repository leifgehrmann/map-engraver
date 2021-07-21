import re

import math

import subprocess

from shapely.geometry import Polygon
from typing import Optional, Tuple

import cairocffi as cairo
from pathlib import Path

import unittest

from mapengraver.canvas import CanvasBuilder, Canvas
from mapengraver.canvas.canvas_unit import CanvasUnit as Cu, CanvasUnit
from mapengraver.graphicshelper import CairoHelper
from tests.canvas.unit_scale import UnitScale


class TestCanvasBuilder(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_svg(self):
        path = Path(__file__).parent.joinpath('output/canvas_builder.pdf')
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_mm(100), Cu.from_mm(100))

        canvas = canvas_builder.build()
        canvas.close()

        assert path.exists()

    def test_png(self):
        path = Path(__file__).parent.joinpath('output/canvas_builder.png')
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_px(100), Cu.from_px(100))
        canvas_builder.set_pixel_scale_factor(2)

        canvas = canvas_builder.build()
        canvas.close()

        assert path.exists()

    def test_setting_alias_modes(self):
        canvas_builder = CanvasBuilder()
        canvas_builder.set_anti_alias_mode(cairo.ANTIALIAS_DEFAULT)
        canvas_builder.set_anti_alias_mode(cairo.ANTIALIAS_NONE)
        canvas_builder.set_anti_alias_mode(cairo.ANTIALIAS_GRAY)
        canvas_builder.set_anti_alias_mode(cairo.ANTIALIAS_SUBPIXEL)
        canvas_builder.set_anti_alias_mode(cairo.ANTIALIAS_FAST)
        canvas_builder.set_anti_alias_mode(cairo.ANTIALIAS_GOOD)
        canvas_builder.set_anti_alias_mode(cairo.ANTIALIAS_BEST)

    def test_invalid_setters(self):
        valid_path = Path(__file__).parent.joinpath('output/valid.png')
        invalid_path = Path(__file__).parent.joinpath('output/invalid.wat')
        with self.assertRaises(RuntimeError):
            canvas_builder = CanvasBuilder()
            canvas_builder.set_size(Cu.from_mm(1), Cu.from_mm(1))
            canvas_builder.set_path(invalid_path)
        with self.assertRaises(RuntimeError):
            canvas_builder = CanvasBuilder()
            canvas_builder.set_path(valid_path)
            canvas_builder.set_size(Cu.from_mm(-1), Cu.from_mm(1))
        with self.assertRaises(RuntimeError):
            canvas_builder = CanvasBuilder()
            canvas_builder.set_path(valid_path)
            canvas_builder.set_size(Cu.from_mm(1), Cu.from_mm(-1))
        with self.assertRaises(RuntimeError):
            canvas_builder = CanvasBuilder()
            canvas_builder.set_path(valid_path)
            canvas_builder.set_size(Cu.from_mm(1), Cu.from_mm(1))
            canvas_builder.set_anti_alias_mode(-1)
        with self.assertRaises(RuntimeError):
            canvas_builder = CanvasBuilder()
            canvas_builder.set_path(valid_path)
            canvas_builder.set_size(Cu.from_mm(1), Cu.from_mm(1))
            canvas_builder.set_anti_alias_mode(7)

    def test_invalid_directory_path(self):
        path = Path(__file__).parent.joinpath(
            'fake_output/canvas_builder_invalid_path.png'
        )
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_px(100), Cu.from_px(100))

        with self.assertRaises(RuntimeError):
            canvas_builder.build()

        assert not path.exists()

    def test_unset_paths(self):
        path = Path(__file__).parent.joinpath(
            'invalid_output_dir/canvas_builder_invalid_path.png'
        )
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_px(100), Cu.from_px(100))

        with self.assertRaises(RuntimeError):
            canvas_builder.build()

        assert not path.exists()

    def test_unset_size(self):
        path = Path(__file__).parent.joinpath(
            'output/canvas_builder_invalid_sizes.png'
        )
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)

        with self.assertRaises(RuntimeError):
            canvas_builder.build()

        assert not path.exists()

    def test_validating_pixel_scale_factor(self):
        path = Path(__file__).parent.joinpath(
            'output/canvas_builder_pixel_scale_factor.svg'
        )
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_px(100), Cu.from_px(100))
        canvas_builder.set_pixel_scale_factor(2)

        with self.assertRaises(RuntimeError):
            canvas_builder.build()

        assert not path.exists()

    """
    Each output format should have a square in the top left corner. This tests
    that the scale is correct, both from the perspective of the canvas (The
    canvas dimensions should match the units), and the polygons drawn (The
    midpoint of the canvas).
    """
    def test_scaling_outputs(self):
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
                    expected_size = Cu.from_unit(4, unit)
                    # Setting to a smaller size to avoid disk space issues
                    canvas_builder.set_size(expected_size, expected_size)
                else:
                    expected_size_in_unit = 100
                    expected_size = CanvasUnit.from_unit(100, unit)
                    canvas_builder.set_size(expected_size, expected_size)

                path = Path(__file__).parent \
                    .joinpath(
                    'output/canvas_builder_%s_%d%s_x%s.%s' %
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
                expected_scale = pixel_scale_factor
                canvas_builder.set_pixel_scale_factor(pixel_scale_factor)

                canvas = canvas_builder.build()
                self.draw_rectangle_top_left(canvas, unit)
                canvas.close()

                assert path.exists()

                actual = self.get_file_dimensions_and_scale(path)
                if surface_type == 'pdf':
                    self.assert_match(
                        expected_size_in_unit, unit, surface_type,
                        1, actual, expected_size.pt
                    )
                elif surface_type == 'svg':
                    self.assert_match(
                        expected_size_in_unit, unit, surface_type,
                        1, actual, expected_size.px
                    )
                elif surface_type == 'png':
                    self.assert_match(
                        expected_size_in_unit, unit, surface_type,
                        pixel_scale_factor, actual, expected_size.px
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
    def get_file_dimensions_and_scale(
            path: Path
    ) -> Tuple[float, float, float]:
        width: float
        height: float
        scale: float
        if path.suffix.lower() == '.pdf':
            pipe = subprocess.Popen(
                [
                    'grep', '-a', 'MediaBox', path.as_posix()
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            stdout, stderr = pipe.communicate()
            stdout_str = str(stdout.decode('utf-8'))
            match = re.search(r'([0-9.]+) ([0-9.]+) ]', stdout_str)
            width = float(match.group(1))
            height = float(match.group(2))
            scale = 1.0
        elif path.suffix.lower() == '.svg':
            pipe = subprocess.Popen(
                [
                    'grep', '-a', '<svg', path.as_posix()
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            stdout, stderr = pipe.communicate()
            stdout_str = str(stdout.decode('utf-8'))
            width_match = re.search(r'width="([0-9.]+)pt"', stdout_str)
            height_match = re.search(r'height="([0-9.]+)pt"', stdout_str)
            width = float(width_match.group(1))
            height = float(height_match.group(1))
            scale = 1.0
        else:
            from PIL import Image
            image = Image.open(path.as_posix())
            width, height = image.size
            scale = CanvasUnit.from_px(float(image.info['dpi'][0])).inches
        return width, height, scale

    @staticmethod
    def assert_match(
            expected_size_in_unit,
            unit,
            surface_type,
            pixel_scale_factor,
            actual: Tuple[float, float, float],
            expected
    ):
        if not math.isclose(
                actual[0],
                expected * pixel_scale_factor,
                rel_tol=1.0
        ):
            raise AssertionError(
                'mismatched-size for %s%s.%s x%s. expected: %f, actual: %f' % (
                    expected_size_in_unit,
                    unit,
                    surface_type,
                    pixel_scale_factor,
                    expected * pixel_scale_factor,
                    actual[0]
                )
            )
        if not math.isclose(
                actual[1],
                expected * pixel_scale_factor,
                rel_tol=1.0
        ):
            raise AssertionError(
                'mismatched-size for %s%s.%s x%s. expected: %f, actual: %f' % (
                    expected_size_in_unit,
                    unit,
                    surface_type,
                    pixel_scale_factor,
                    expected * pixel_scale_factor,
                    actual[1]
                )
            )
        if not math.isclose(
                actual[2],
                pixel_scale_factor,
                rel_tol=0.01
        ):
            raise AssertionError(
                'mismatched-scale for %s%s.%s x%s. expected: %f, actual: %f' % (
                    expected_size_in_unit,
                    unit,
                    surface_type,
                    pixel_scale_factor,
                    pixel_scale_factor,
                    actual[2],
                )
            )

    def test_unit_scale(self):
        surface_types = ['png', 'svg', 'pdf']
        for surface_type in surface_types:
            path = Path(__file__).parent\
                .joinpath('output/canvas_builder_unit_scale.%s' % surface_type)
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
