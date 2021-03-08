from pathlib import Path

import unittest

from mapengraver.canvas import CanvasBuilder
from mapengraver.canvas.canvas_unit import CanvasUnit
from mapengraver.drawable.images.svg import Svg
from mapengraver.drawable.layout.margins import Margins


class TestSvg(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_output(self):
        path = Path(__file__).parent.joinpath('output/svg.svg')
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(20, 15, 'cm')

        canvas = canvas_builder.build()

        canvas.context.save()
        canvas.context.translate(CanvasUnit.from_cm(1).pt, CanvasUnit.from_cm(1).pt)
        canvas.context.scale(2, 2)
        svg = Svg(Path(__file__).parent.joinpath('test_svg.svg'))
        svg.draw(canvas)
        canvas.context.restore()

        canvas.close()

        assert path.exists()
