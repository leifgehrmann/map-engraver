from typing import List, Optional, Tuple, Union

from shapely.geometry import Polygon, MultiPolygon

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.drawable import Drawable
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer


class StripeFilledPolygonDrawer(Drawable):
    stroke_width: Optional[CanvasUnit]
    width_arr: List[float]
    color_arr: List[Optional[Tuple[float, float, float, float]]]
    origin: Tuple[float, float]
    angle: float
    geoms: List[Union[Polygon, MultiPolygon]]

    def __init__(self):
        self.geoms = []
        self.width_arr = [1]
        self.color_arr = [(0, 0, 0, 1)]
        self.angle = 0
        self.origin = (0, 0)

    def draw(self, canvas: Canvas):
        if len(self.width_arr) != len(self.color_arr):
            raise ValueError(
                'length of width_arr is not the same as color_arr'
            )
        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = self.color_arr[0]
        polygon_drawer.polygons = self.geoms
        polygon_drawer.draw(canvas)
