from pathlib import Path

import unittest

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.graphicshelper.cairo_svg_helper import CairoSvgHelper
from tests.utils import svg_has_style_attr


class TestCairoSvgHelper(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/')\
            .mkdir(parents=True, exist_ok=True)

    def test_outputs_expected_lines(self):
        path = Path(__file__).parent.joinpath(
            'output/cairo_svg_helper_outputs_expected_lines.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_pt(100), Cu.from_pt(100))

        canvas = canvas_builder.build()

        CairoSvgHelper.execute_svg_path_in_cairo(
            canvas.context,
            'M10 10 90 10'  # Top line
            'M90,90L10,90'  # Bottom line
            'M10 50L50,10,90,50,50,90'  # Inner Diamond
        )
        canvas.context.stroke()

        canvas.close()

        assert path.exists()

        with open(path, 'r') as file:
            data = file.read()
            assert svg_has_style_attr(
                data, 'path', 'd',
                'M 10 10 L 90 10 '  # Top line
                'M 90 90 L 10 90 '  # Bottom line
                'M 10 50 L 50 10 L 90 50 L 50 90'  # Inner Diamond
            )
