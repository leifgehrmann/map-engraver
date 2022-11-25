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

    def test_unsupported_graphics(self):
        input_path = Path(__file__).parent
        with self.assertRaises(NotImplementedError):
            Bitmap(input_path.joinpath('test_bitmap_unsupported.jpg'))

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

        with open(output_path, 'r') as file:
            data = file.read()
            assert data.find('matrix(0.75,0,0,0.75,37.5,37.5)') != -1
            assert data.find('matrix(0.375,0,0,0.375,37.5,112.5)') != -1
            assert data.find('matrix(0.375,0,0,0.375,37.5,150)') != -1
            assert data.find('matrix(0.375,0,0,0.75,112.5,112.5)') != -1
            assert data.find(
                'matrix(0.265165,0.265165,-0.53033,0.53033,112.5,187.5)'
            ) != -1
            assert data.find('matrix(0.75,0,0,0.75,225,37.5)') != -1
            assert data.find('matrix(0.375,0,0,0.375,225,112.5)') != -1
            assert data.find('matrix(0.375,0,0,0.375,225,150)') != -1
            assert data.find('matrix(0.375,0,0,0.75,300,112.5)') != -1
            assert data.find(
                'matrix(0.265165,0.265165,-0.53033,0.53033,300,187.5)'
            ) != -1
            assert data.find('matrix(1,0,0,1,450,37.5)') != -1
            assert data.find('matrix(0.5,0,0,0.5,450,137.5)') != -1
            assert data.find('matrix(0.5,0,0,0.5,450,187.5)') != -1
            assert data.find('matrix(0.5,0,0,1,550,137.5)') != -1
            assert data.find(
                'matrix(0.353553,0.353553,-0.707107,0.707107,550,237.5)'
            ) != -1
