import unittest
from pathlib import Path

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_unit import CanvasUnit


class TestGeotiffDisplay(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_geotiff_display(self):
        path = Path(__file__).parent.joinpath(
            'output/geotiff_display.svg'
        )
        path.unlink(missing_ok=True)

        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(
            CanvasUnit.from_px(100),
            CanvasUnit.from_px(200),
        )
        canvas = canvas_builder.build()

        # Todo

        canvas.close()
