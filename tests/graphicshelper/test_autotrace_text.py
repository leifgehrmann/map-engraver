from pathlib import Path

import unittest

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate as Cc
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.data.pango.layout import Layout
from map_engraver.graphicshelper.autotrace_text import AutotraceText


class TestAutotraceText(unittest.TestCase):
    def setUp(self):
        output_path = Path(__file__).parent.joinpath('output')
        output_path.mkdir(parents=True, exist_ok=True)

    def test_fails_if_cache_directory_not_set(self):
        pass

    def test_layout_is_converted_to_svg_path(self):
        path = Path(__file__).parent.joinpath(
            'output/autotrace_text_text_is_converted_to_strokes.png'
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

        svg_path = AutotraceText.convert_pango_layout_to_svg_draw_commands(
            layout.pango_layout
        )

        assert isinstance(svg_path, str)
        assert svg_path.startswith('M')
        assert 'L' in svg_path

        canvas.close()
