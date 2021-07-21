from pathlib import Path

import unittest

from mapengraver.canvas import CanvasBuilder
from mapengraver.canvas.canvas_unit import CanvasUnit as Cu
from mapengraver.drawable.images.svg import Svg
from mapengraver.drawable.layout.background import Background


class TestSvg(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_calculating_dimensions(self):
        svg = Svg(Path(__file__).parent.joinpath('test_svg.svg'))
        width, height = svg.read_svg_size()
        assert width.pt == 100
        assert height.pt == 60

    def test_output(self):
        path = Path(__file__).parent.joinpath('output/svg.svg')
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(
            Cu.from_cm(4),
            Cu.from_cm(4)
        )

        canvas = canvas_builder.build()

        background = Background()
        background.color = (1, 0.8, 0.8, 1)
        background.draw(canvas)

        # No scaling
        svg = Svg(Path(__file__).parent.joinpath('test_svg.svg'))
        svg.origin_on_canvas = (Cu.from_cm(1).pt, Cu.from_cm(1).pt)
        svg.draw(canvas)

        # Scale 2x by height
        svg = Svg(Path(__file__).parent.joinpath('test_svg.svg'))
        svg.origin_on_canvas = (Cu.from_cm(5).pt, Cu.from_cm(1).pt)
        svg.width_on_canvas = Cu.from_cm(3).pt
        svg.draw(canvas)

        # Scale 2x by height
        svg = Svg(Path(__file__).parent.joinpath('test_svg.svg'))
        svg.origin_on_canvas = (Cu.from_cm(1).pt, Cu.from_cm(4).pt)
        svg.height_on_canvas = Cu.from_cm(1).pt
        svg.draw(canvas)

        # Scale without ratio preservation
        svg = Svg(Path(__file__).parent.joinpath('test_svg.svg'))
        svg.origin_on_canvas = (Cu.from_cm(5).pt, Cu.from_cm(4).pt)
        svg.width_on_canvas = Cu.from_cm(3).pt
        svg.height_on_canvas = Cu.from_cm(1).pt
        svg.draw(canvas)

        canvas.close()

        assert path.exists()
