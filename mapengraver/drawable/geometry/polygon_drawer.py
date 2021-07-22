from typing import List, Optional, Tuple

from shapely.geometry import Polygon

from mapengraver.canvas import Canvas
from mapengraver.canvas.canvas_unit import CanvasUnit
from mapengraver.drawable.drawable import Drawable
from mapengraver.graphicshelper import CairoHelper


class PolygonDrawer(Drawable):
    stroke_width: Optional[CanvasUnit]
    stroke_color: Optional[Tuple[float, float, float, float]]
    fill_color: Optional[Tuple[float, float, float, float]]
    polygons: List[Polygon]

    def __init__(self):
        self.polygons = []
        self.fill_color = (1, 1, 1, 1)
        self.stroke_color = (0, 0, 0, 1)
        self.stroke_width = None

    def _has_fill(self) -> bool:
        return self.fill_color is not None

    def _has_stroke(self) -> bool:
        return self.stroke_width is not None and self.stroke_color is not None

    def draw(self, canvas: Canvas):
        for polygon in self.polygons:
            CairoHelper.draw_polygon(canvas.context, polygon)
            if self._has_fill() and self._has_stroke():
                canvas.context.set_source_rgba(*self.fill_color)
                canvas.context.fill_preserve()
            elif self._has_fill():
                canvas.context.set_source_rgba(*self.fill_color)
                canvas.context.fill()
            if self._has_stroke():
                canvas.context.set_line_width(self.stroke_width.pt)
                canvas.context.set_source_rgba(*self.stroke_color)
                canvas.context.stroke()
