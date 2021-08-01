from typing import List, Optional, Tuple, Union

from shapely.geometry import Polygon, MultiPolygon

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.drawable import Drawable
from map_engraver.graphicshelper import CairoHelper


class PolygonDrawer(Drawable):
    stroke_width: Optional[CanvasUnit]
    stroke_color: Optional[Tuple[float, float, float, float]]
    fill_color: Optional[Tuple[float, float, float, float]]
    geoms: List[Union[Polygon, MultiPolygon]]

    def __init__(self):
        self.polygons = []
        self.fill_color = None
        self.stroke_color = (0, 0, 0, 1)
        self.stroke_width = None

    def _has_fill(self) -> bool:
        return self.fill_color is not None

    def _has_stroke(self) -> bool:
        return self.stroke_width is not None and self.stroke_color is not None

    def draw(self, canvas: Canvas):
        for geom in self.geoms:
            if type(geom) is MultiPolygon:
                for sub_geom in geom.geoms:
                    self.draw_polygon(canvas, sub_geom)
            else:
                self.draw_polygon(canvas, geom)

    def draw_polygon(self, canvas: Canvas, polygon: Polygon):
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
