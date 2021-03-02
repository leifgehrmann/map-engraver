from pathlib import Path

import unittest

from mapengraver.canvas import CanvasBuilder


class TestCanvasBuilder(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_svg(self):
        path = Path(__file__).parent.joinpath('output/canvas_builder.pdf')
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(100, 100, 'mm')

        canvas = canvas_builder.build()
        canvas.close()

        assert path.exists()

    def test_png(self):
        path = Path(__file__).parent.joinpath('output/canvas_builder.png')
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(100, 100, 'px')
        canvas_builder.set_pixel_scale_factor(2)

        canvas = canvas_builder.build()
        canvas.close()

        assert path.exists()
