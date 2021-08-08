from pathlib import Path

import unittest

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate as Cc
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.data.pango.layout import Layout
from map_engraver.drawable.text.pango_drawer import PangoDrawer


class TestPangoDrawer(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_layout_is_drawn(self):
        path = Path(__file__).parent.joinpath(
            'output/pango_drawer_layout_is_drawn.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        layout = Layout(canvas)
        layout.position = Cc.from_pt(10, 10)
        layout.color = (0, 0, 1, 0.5)
        layout.width = Cu.from_pt(80)
        layout.height = Cu.from_pt(80)
        layout.set_markup(
            '<span font="10px">Hello '
            '<span font="italic" color="#FF0000FF">World</span>'
            '</span>'
        )

        drawer = PangoDrawer()
        drawer.pango_objects = [layout]
        drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert data.find('<g style="fill:rgb(0%,0%,100%);fill-opacity:0.5;">') != -1
            assert data.find('xlink:href="#glyph0-1" x="10"') != -1
            assert data.find('<g style="fill:rgb(100%,0%,0%);fill-opacity:1;">') != -1
            assert data.find('xlink:href="#glyph1-5"') != -1
