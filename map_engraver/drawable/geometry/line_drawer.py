from typing import List, Optional, Tuple, Union

from shapely.geometry import LineString, MultiLineString

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.drawable import Drawable
from map_engraver.graphicshelper import CairoHelper


class LineDrawer(Drawable):
    stroke_width: Optional[CanvasUnit]
    stroke_color: Optional[Tuple[float, float, float, float]]
    stroke_dashes: Optional[Tuple[List[CanvasUnit], Optional[CanvasUnit]]]
    stroke_line_cap: Optional[int]  # See cairocffi constants: LINE_CAP_*
    stroke_line_join: Optional[int]  # See cairocffi constants: LINE_JOIN_*
    geoms: List[Union[LineString, MultiLineString]]

    def __init__(self):
        self.stroke_color = (0, 0, 0, 1)
        self.stroke_width = CanvasUnit.from_pt(1)
        self.stroke_dashes = None
        self.stroke_line_cap = None
        self.stroke_line_join = None

    def draw(self, canvas: Canvas):
        if self.stroke_width is not None:
            canvas.context.set_line_width(self.stroke_width.pt)
        if self.stroke_color is not None:
            canvas.context.set_source_rgba(*self.stroke_color)
        if self.stroke_dashes is not None:
            dashes = list(map(lambda d: d.pt, self.stroke_dashes[0]))
            offset_unit = self.stroke_dashes[1]
            offset = offset_unit.pt if offset_unit is not None else 0
            canvas.context.set_dash(dashes, offset)
        if self.stroke_line_cap is not None:
            canvas.context.set_line_cap(self.stroke_line_cap)
        if self.stroke_line_join is not None:
            canvas.context.set_line_join(self.stroke_line_join)
        for geom in self.geoms:
            if type(geom) is MultiLineString:
                for sub_geom in geom.geoms:
                    LineDrawer.draw_line_string(canvas, sub_geom)
            else:
                LineDrawer.draw_line_string(canvas, geom)

    @staticmethod
    def draw_line_string(canvas: Canvas, line_string: LineString):
        CairoHelper.draw_line_string(canvas.context, line_string)
        canvas.context.stroke()
