from pathlib import Path

import unittest

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.drawable.text.pango_drawer import PangoDrawer


class TestPangoDrawer(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_temp(self):
        path = Path(__file__).parent.joinpath(
            'output/pango_drawer_temp.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        drawer = PangoDrawer()
        drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert data.find('#glyph0-7') != -1
            assert data.find('#glyph1-1') != -1
