from typing import List, Optional, Tuple, Union

from shapely.geometry import LineString, MultiLineString

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.drawable import Drawable
from map_engraver.graphicshelper import CairoHelper


class LineDrawer(Drawable):
    stroke_width: Optional[CanvasUnit]
    stroke_color: Optional[Tuple[float, float, float, float]]
    geoms: List[Union[LineString, MultiLineString]]

    def __init__(self):
        self.stroke_color = (0, 0, 0, 1)
        self.stroke_width = CanvasUnit.from_pt(1)

    def draw(self, canvas: Canvas):
        for geom in self.geoms:
            if type(geom) is MultiLineString:
                for sub_geom in geom.geoms:
                    self.draw_line_string(canvas, sub_geom)
            else:
                self.draw_line_string(canvas, geom)

    def draw_line_string(self, canvas: Canvas, line_string: LineString):
        CairoHelper.draw_line_string(canvas.context, line_string)
        canvas.context.set_line_width(self.stroke_width.pt)
        canvas.context.set_source_rgba(*self.stroke_color)
        canvas.context.stroke()
