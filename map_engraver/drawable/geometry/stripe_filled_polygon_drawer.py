from typing import List, Optional, Tuple, Union

from shapely.geometry import Polygon, MultiPolygon

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.drawable import Drawable
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer


class StripeFilledPolygonDrawer(Drawable):
    width_arr: List[CanvasUnit]
    color_arr: List[Optional[Tuple[float, float, float, float]]]
    origin: CanvasCoordinate
    angle: float
    geoms: List[Union[Polygon, MultiPolygon]]

    def __init__(self):
        self.geoms = []
        self.stripe_widths = [CanvasUnit.from_pt(1)]
        self.stripe_colors = [(0, 0, 0, 1)]
        self.angle = 0
        self.origin = CanvasCoordinate.origin()

    def draw(self, canvas: Canvas):
        if len(self.stripe_widths) != len(self.stripe_colors):
            raise ValueError(
                'length of width_arr is not the same as color_arr'
            )
        if len(self.stripe_widths) == 0:
            raise ValueError(
                'width_arr must contain at least one value'
            )
        if len(self.stripe_widths) == 1:
            if self.stripe_colors[0] is None:
                return
            polygon_drawer = PolygonDrawer()
            polygon_drawer.fill_color = self.stripe_colors[0]
            polygon_drawer.geoms = self.geoms
            polygon_drawer.draw(canvas)
            return
