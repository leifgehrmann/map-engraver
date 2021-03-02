from pathlib import Path

import unittest

from mapengraver.canvas import CanvasBuilder
from mapengraver.drawable.layout.background import Background


class TestBackground(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_outputs_color(self):
        path = Path(__file__).parent.joinpath('output/background.svg')
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(100, 100, 'mm')

        canvas = canvas_builder.build()

        background = Background()
        background.color = (0.5, 0.5, 0.5)
        background.draw(canvas)

        canvas.close()

        assert path.exists()
