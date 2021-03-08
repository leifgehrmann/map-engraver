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
        self.origin_on_canvas = (0, 0)
        self.width_on_canvas = None
        self.height_on_canvas = None

    def read_svg_size(self) -> Tuple[CanvasUnit, CanvasUnit]:
        svg_surface = SvgSurface(self.path)
        return (
            CanvasUnit.from_pt(svg_surface.svg_width),
            CanvasUnit.from_pt(svg_surface.svg_height)
        )

    def progress(self):
        pass

    def draw(self, canvas: Canvas):
        svg_surface = SvgSurface(self.path)
        svg_surface.set_position(*self.origin_on_canvas)
        if self.width_on_canvas is not None and \
                self.height_on_canvas is not None:
            svg_surface.set_width(self.width_on_canvas, preserve_ratio=False)
            svg_surface.set_height(self.height_on_canvas, preserve_ratio=False)
        elif self.width_on_canvas is not None:
            svg_surface.set_width(self.width_on_canvas, preserve_ratio=True)
        elif self.height_on_canvas is not None:
            svg_surface.set_height(self.height_on_canvas, preserve_ratio=True)
        svg_surface.draw(canvas.context, canvas.surface)
