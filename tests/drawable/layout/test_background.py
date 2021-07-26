from pathlib import Path

import unittest

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.drawable.layout.background import Background


class TestBackground(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_outputs_color(self):
        path = Path(__file__).parent.joinpath('output/background.svg')
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_px(100), Cu.from_px(100))

        canvas = canvas_builder.build()

        background = Background()
        background.color = (0.5, 0.5, 0.5)
        background.draw(canvas)

        canvas.close()

        assert path.exists()
