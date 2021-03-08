from pathlib import Path

import unittest

from mapengraver.canvas import CanvasBuilder
from mapengraver.canvas.canvas_unit import CanvasUnit
from mapengraver.drawable.layout.margins import Margins


class TestMargins(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_output(self):
        path = Path(__file__).parent.joinpath('output/margins.svg')
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(20, 15, 'cm')

        canvas = canvas_builder.build()

        margins = Margins()
        margins.set_margins(CanvasUnit.from_cm(4))
        margins.margin_top = CanvasUnit.from_cm(3)
        margins.margin_bottom = CanvasUnit.from_cm(3)
        margins.fill_color = (1, 0.9, 1, 1)
        margins.draw(canvas)

        margins = Margins()
        margins.set_margins(CanvasUnit.from_cm(3))
        margins.margin_top = CanvasUnit.from_cm(2)
        margins.margin_bottom = CanvasUnit.from_cm(2)
        margins.stroke_width = CanvasUnit.from_mm(1)
        margins.stroke_color = (0.5, 0.5, 0.1, 1)
        margins.fill_color = (1, 1, 0.9, 1)
        margins.draw(canvas)

        canvas.close()

        assert path.exists()
