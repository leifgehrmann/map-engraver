from pathlib import Path

import unittest

from cairocffi.constants import LINE_CAP_ROUND
from cairocffi.constants import LINE_JOIN_ROUND

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate as Cc
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.data.pango.layout import Layout
from map_engraver.drawable.text.pango_stroke_drawer import PangoStrokeDrawer
from tests.utils import svg_has_style_attr, svg_has_tag


class TestPangoStrokeDrawer(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_layout_is_drawn(self):
        path = Path(__file__).parent.joinpath(
            'output/pango_stroke_drawer_layout_is_drawn.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        layout = Layout(canvas)
        layout.position = Cc.from_pt(10, 10)
        layout.width = Cu.from_pt(80)
        layout.height = Cu.from_pt(80)
        layout.apply_markup(
            '<span font="sans serif 10px">Hello '
            '<span font="italic">World</span>'
            '</span>'
        )

        drawer = PangoStrokeDrawer()
        drawer.stroke_color = (1, 0, 0, 1)
        drawer.stroke_width = Cu.from_pt(0.5)
        drawer.stroke_line_join = LINE_JOIN_ROUND
        drawer.stroke_line_cap = LINE_CAP_ROUND
        drawer.pango_objects = [layout]
        drawer.draw(canvas)

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert not svg_has_tag(data, 'g')
            assert svg_has_style_attr(data, 'path', 'fill', 'none')
            assert svg_has_style_attr(data, 'path', 'stroke-linecap', 'round')
            assert svg_has_style_attr(data, 'path', 'stroke-linejoin', 'round')
            assert svg_has_style_attr(data, 'path', 'stroke-width', '0.5')
            assert svg_has_style_attr(data, 'path', 'd', 'M.*', escape=False)
            assert svg_has_style_attr(
                data, 'path', 'transform',
                'matrix\\(1, *0, *0, *1, *10, *10\\)', escape=False
            )
