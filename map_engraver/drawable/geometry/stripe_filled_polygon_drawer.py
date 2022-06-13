import math

from typing import List, Optional, Tuple, Union

from shapely.geometry import Polygon, MultiPolygon

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.drawable import Drawable
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer
from map_engraver.drawable.geometry.stripe_utils import \
    create_polygons_from_stripe_data


class StripeFilledPolygonDrawer(Drawable):
    stripe_widths: List[CanvasUnit]
    stripe_colors: List[Optional[Tuple[float, float, float, float]]]
    stripe_origin: CanvasCoordinate
    stripe_angle: float
    stripe_line: Tuple[Tuple[float, float], Tuple[float, float]]
    geoms: List[Union[Polygon, MultiPolygon]]

    def __init__(self):
        self.geoms = []
        self.stripe_widths = [CanvasUnit.from_pt(1)]
        self.stripe_colors = [(0, 0, 0, 1)]
        self.stripe_angle = 0
        self.stripe_origin = CanvasCoordinate.origin()

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

        for stripe_width in self.stripe_widths:
            if stripe_width.pt <= 0:
                raise ValueError(
                    'width_arr must be a positive non-zero length'
                )

        # Convert class-based inputs into floating point values.
        stripe_line = (
            self.stripe_origin.pt,
            (math.cos(self.stripe_angle), math.sin(self.stripe_angle))
        )
        stripe_widths_pt = list(map(
            lambda stripe: stripe.pt,
            self.stripe_widths
        ))
        stripe_visible = list(map(
            lambda stripe_color: stripe_color is not None,
            self.stripe_colors
        ))

        # Create stripes out of every geom.
        geoms_per_stripe = [[] for _ in range(len(self.stripe_widths))]
        for geom in self.geoms:
            new_geoms_per_stripe = create_polygons_from_stripe_data(
                geom,
                stripe_line,
                stripe_widths_pt,
                stripe_visible
            )
            for (stripe_index, new_geom_for_stripe) in \
                    enumerate(new_geoms_per_stripe):
                if new_geom_for_stripe is None:
                    continue
                geoms_per_stripe[stripe_index].append(new_geom_for_stripe)

        # Then we draw each stripe using the defined colors.
        for (stripe_index, geoms_for_stripe) in enumerate(geoms_per_stripe):
            if len(geoms_for_stripe) == 0:
                continue
            polygon_drawer = PolygonDrawer()
            polygon_drawer.fill_color = self.stripe_colors[stripe_index]
            polygon_drawer.geoms = geoms_per_stripe[stripe_index]
            polygon_drawer.draw(canvas)
