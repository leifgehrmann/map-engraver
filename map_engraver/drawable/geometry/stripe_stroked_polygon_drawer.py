import math

from typing import List, Optional, Tuple, Union

from shapely.geometry import Polygon, MultiPolygon

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.drawable import Drawable
from map_engraver.drawable.geometry.line_drawer import LineDrawer
from map_engraver.drawable.geometry.stripe_utils import \
    create_line_strings_from_stripe_data


class StripeStrokedPolygonDrawer(Drawable):
    stripe_widths: List[CanvasUnit]
    stripe_stroke_widths: List[Optional[CanvasUnit]]
    stripe_colors: List[Optional[Tuple[float, float, float, float]]]
    stripe_origin: CanvasCoordinate
    stripe_angle: float
    stripe_line: Tuple[Tuple[float, float], Tuple[float, float]]
    geoms: List[Union[Polygon, MultiPolygon]]

    def __init__(self):
        self.geoms = []
        self.stripe_widths = [CanvasUnit.from_pt(1)]
        self.stripe_stroke_widths = [CanvasUnit.from_pt(1)]
        self.stripe_colors = [(0, 0, 0, 1)]
        self.stripe_angle = 0
        self.stripe_origin = CanvasCoordinate.origin()

    def draw(self, canvas: Canvas):
        if len(self.stripe_widths) != len(self.stripe_colors):
            raise ValueError(
                'length of stripe_widths is not the same as stripe_colors'
            )

        if len(self.stripe_widths) != len(self.stripe_stroke_widths):
            raise ValueError(
                'length of stripe_widths is not the same as '
                'stripe_stroke_widths'
            )

        if len(self.stripe_widths) == 0:
            raise ValueError(
                'stripe_widths must contain at least one value'
            )

        for stripe_width in self.stripe_widths:
            if stripe_width.pt <= 0:
                raise ValueError(
                    'stripe_widths must be a positive non-zero length'
                )

        for stripe_stroke_width in self.stripe_stroke_widths:
            if stripe_stroke_width is not None and stripe_stroke_width.pt <= 0:
                raise ValueError(
                    'stripe_stroke_widths must be a positive non-zero length'
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

        def is_stripe_visible(stripe_info):
            stripe_color = stripe_info[0]
            stripe_stroke_width = stripe_info[1]
            return stripe_color is not None and \
                stripe_stroke_width is not None and \
                stripe_stroke_width.pt > 0

        stripe_visible = list(map(
            is_stripe_visible,
            zip(self.stripe_colors, self.stripe_stroke_widths)
        ))

        # Create stripes out of every geom.
        geoms_per_stripe = [[] for _ in range(len(self.stripe_widths))]
        for geom in self.geoms:
            new_geoms_per_stripe = create_line_strings_from_stripe_data(
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
            line_drawer = LineDrawer()
            line_drawer.stroke_color = self.stripe_colors[stripe_index]
            line_drawer.stroke_width = self.stripe_stroke_widths[stripe_index]
            line_drawer.geoms = geoms_per_stripe[stripe_index]
            line_drawer.draw(canvas)
