import math

from pathlib import Path

import unittest

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate as Cc
from map_engraver.drawable.images.bitmap import Bitmap
from map_engraver.drawable.layout.background import Background


class TestBitmap(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_calculating_dimensions(self):
        input_path = Path(__file__).parent
        bitmap = Bitmap(input_path.joinpath('test_bitmap_no_px_per_in.png'))
        width, height = bitmap.bitmap_size
        assert width.px == 200
        assert height.px == 100

        bitmap = Bitmap(input_path.joinpath('test_bitmap_96_px_per_in.png'))
        width, height = bitmap.bitmap_size
        assert width.px == 200
        assert height.px == 100

        bitmap = Bitmap(input_path.joinpath('test_bitmap_72_px_per_in.png'))
        width, height = bitmap.bitmap_size
        assert width.pt == 200
        assert height.pt == 100

    def test_scale_and_dpi(self):
        input_path = Path(__file__).parent
        output_path = Path(__file__).parent.joinpath('output/bitmap_scale.svg')
        output_path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(output_path)
        canvas_builder.set_size(
            Cu.from_px(1000),
            Cu.from_px(700)
        )

        canvas = canvas_builder.build()

        background = Background()
        background.color = (1, 0.8, 0.8, 1)
        background.draw(canvas)

        # No resolution info (default to 96px per inch)
        bitmap = Bitmap(input_path.joinpath('test_bitmap_no_px_per_in.png'))
        bitmap.position = Cc.from_px(50, 50)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_no_px_per_in.png'))
        bitmap.position = Cc.from_px(50, 150)
        bitmap.width = Cu.from_px(100)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_no_px_per_in.png'))
        bitmap.position = Cc.from_px(50, 200)
        bitmap.height = Cu.from_px(50)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_no_px_per_in.png'))
        bitmap.position = Cc.from_px(150, 150)
        bitmap.width = Cu.from_px(100)
        bitmap.height = Cu.from_px(100)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_no_px_per_in.png'))
        bitmap.bitmap_origin = Cc.from_px(100, 50)
        bitmap.position = Cc.from_px(150, 250 + math.sqrt(100 * 100 / 2))
        bitmap.rotation = math.pi / 4
        bitmap.width = Cu.from_px(100)
        bitmap.height = Cu.from_px(100)
        bitmap.draw(canvas)

        # 96 px per inch
        bitmap = Bitmap(input_path.joinpath('test_bitmap_96_px_per_in.png'))
        bitmap.position = Cc.from_px(300, 50)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_96_px_per_in.png'))
        bitmap.position = Cc.from_px(300, 150)
        bitmap.width = Cu.from_px(100)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_96_px_per_in.png'))
        bitmap.position = Cc.from_px(300, 200)
        bitmap.height = Cu.from_px(50)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_96_px_per_in.png'))
        bitmap.position = Cc.from_px(400, 150)
        bitmap.width = Cu.from_px(100)
        bitmap.height = Cu.from_px(100)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_96_px_per_in.png'))
        bitmap.bitmap_origin = Cc.from_px(100, 50)
        bitmap.position = Cc.from_px(400, 250 + math.sqrt(100 * 100 / 2))
        bitmap.rotation = math.pi / 4
        bitmap.width = Cu.from_px(100)
        bitmap.height = Cu.from_px(100)
        bitmap.draw(canvas)

        # No resolution info (default to 96px per inch)
        bitmap = Bitmap(input_path.joinpath('test_bitmap_72_px_per_in.png'))
        bitmap.position = Cc.from_px(600, 50)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_72_px_per_in.png'))
        bitmap.position = Cc(Cu.from_px(600), Cu.from_px(50) + Cu.from_pt(100))
        bitmap.width = Cu.from_pt(100)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_72_px_per_in.png'))
        bitmap.position = Cc(Cu.from_px(600), Cu.from_px(50) + Cu.from_pt(150))
        bitmap.height = Cu.from_pt(50)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_72_px_per_in.png'))
        bitmap.position = Cc(
            Cu.from_px(600) + Cu.from_pt(100),
            Cu.from_px(50) + Cu.from_pt(100)
        )
        bitmap.width = Cu.from_pt(100)
        bitmap.height = Cu.from_pt(100)
        bitmap.draw(canvas)

        bitmap = Bitmap(input_path.joinpath('test_bitmap_72_px_per_in.png'))
        bitmap.bitmap_origin = Cc.from_px(100, 50)
        bitmap.position = Cc(
            Cu.from_px(600) + Cu.from_pt(100),
            Cu.from_px(50) + Cu.from_pt(200 + math.sqrt(100 * 100 / 2))
        )
        bitmap.rotation = math.pi / 4
        bitmap.width = Cu.from_pt(100)
        bitmap.height = Cu.from_pt(100)
        bitmap.draw(canvas)

        canvas.close()

        assert output_path.exists()
        # Todo: assert sizes
    #
    # def test_output_translate_rotate_scale(self):
    #     path = Path(__file__).parent.joinpath('output/svg_trs.svg')
    #     path.unlink(missing_ok=True)
    #     canvas_builder = CanvasBuilder()
    #     canvas_builder.set_path(path)
    #     canvas_builder.set_size(
    #         Cu.from_cm(4),
    #         Cu.from_cm(4)
    #     )
    #
    #     canvas = canvas_builder.build()
    #
    #     background = Background()
    #     background.color = (0.8, 1, 0.8, 1)
    #     background.draw(canvas)
    #
    #     svg = Svg(Path(__file__).parent.joinpath('test_svg_grid.svg'))
    #     svg_size = svg.read_svg_size()
    #     # Should set the origin of the image to the center.
    #     svg.svg_origin = Cc(svg_size[0] / 2, svg_size[1] / 2)
    #     # Should position the image in the center of the screen.
    #     svg.position = Cc.from_cm(2, 2)
    #     # Should rotate the image clock-wise.
    #     svg.rotation = math.pi / 8
    #     # Resizes the image to almost the size of the canvas, but not exactly.
    #     svg.width = Cu.from_cm(3)
    #     svg.height = Cu.from_cm(3)
    #     svg.draw(canvas)
    #
    #     canvas.close()
    #
    #     assert path.exists()
