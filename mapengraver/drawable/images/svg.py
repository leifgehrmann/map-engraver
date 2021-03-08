from typing import Tuple

from pathlib import Path

from mapengraver.canvas import Canvas
from mapengraver.canvas.canvas_unit import CanvasUnit
from mapengraver.drawable.drawable import Drawable
from mapengraver.graphicshelper.svg_surface import SvgSurface
from mapengraver.logging.progressable import ProgressObservable


class Svg(Drawable, ProgressObservable):

    def __init__(self, path: Path):
        self.path = path
        self.canvas_origin = (0, 0)
        self.svg_origin = (0, 0)
        self.width = None
        self.height = None

    def parse_svg_size(self) -> Tuple[CanvasUnit, CanvasUnit]:
        svg_surface = SvgSurface(self.path)
        return (
            CanvasUnit.from_pt(svg_surface.svg_width),
            CanvasUnit.from_pt(svg_surface.svg_height)
        )

    def progress(self):
        pass

    def draw(self, canvas: Canvas):
        svg_surface = SvgSurface(self.path)
        svg_surface.set_width(100)
        # Read dimensions
        svg_surface.draw(canvas.context, canvas.surface)


