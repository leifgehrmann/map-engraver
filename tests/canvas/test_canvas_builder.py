import cairocffi as cairo
from pathlib import Path

import unittest

from mapengraver.canvas import CanvasBuilder
from mapengraver.canvas.canvas_unit import CanvasUnit as Cu


class TestCanvasBuilder(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
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
        path = Path(__file__).parent.joinpath('output/canvas_builder.wat')
        with self.assertRaises(RuntimeError):
            canvas_builder = CanvasBuilder()
            canvas_builder.set_size(Cu.from_mm(1), Cu.from_mm(1))
            canvas_builder.set_path(path)
        with self.assertRaises(RuntimeError):
            canvas_builder = CanvasBuilder()
            canvas_builder.set_path(path)
            canvas_builder.set_size(Cu.from_mm(-1), Cu.from_mm(1))
        with self.assertRaises(RuntimeError):
            canvas_builder = CanvasBuilder()
            canvas_builder.set_path(path)
            canvas_builder.set_size(Cu.from_mm(1), Cu.from_mm(-1))
        with self.assertRaises(RuntimeError):
            canvas_builder = CanvasBuilder()
            canvas_builder.set_path(path)
            canvas_builder.set_size(Cu.from_mm(1), Cu.from_mm(1))
            canvas_builder.set_anti_alias_mode(-1)
        with self.assertRaises(RuntimeError):
            canvas_builder = CanvasBuilder()
            canvas_builder.set_path(path)
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
