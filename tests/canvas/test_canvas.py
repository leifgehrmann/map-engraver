import cairocffi
from pathlib import Path

import unittest

from mapengraver.canvas import Canvas


class TestCanvas(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/').mkdir(parents=True, exist_ok=True)

    def test_svg(self):
        path = Path(__file__).parent.joinpath('output/canvas.svg')
        path.unlink(missing_ok=True)
        canvas = Canvas(path, 'svg', 100, 100)
        canvas.close()

        with open(path, 'r') as file:
            data = file.read()
            assert data.find('100pt') != -1

    def test_pdf(self):
        path = Path(__file__).parent.joinpath('output/canvas.pdf')
        path.unlink(missing_ok=True)
        canvas = Canvas(path, 'pdf', 100, 100)
        canvas.close()

        assert path.exists()

    def test_png(self):
        path = Path(__file__).parent.joinpath('output/canvas.png')
        path.unlink(missing_ok=True)
        canvas = Canvas(path, 'png', 100, 100)
        canvas.set_scale(0.5)
        canvas.set_antialias_mode(cairocffi.ANTIALIAS_NONE)
        canvas.close()

        assert path.exists()
