import math
from shapely.geometry import Polygon, LineString

from typing import Tuple

from map_engraver.data.math.trig import scalar_between_lines_origin_and_projected_point, line_intersection

Vector = Tuple[float, float]
Coord = Tuple[float, float]
UnitVector = Tuple[float, float]
# A line, defined by two vectors, an origin, and direction.
Line = Tuple[Vector, Vector]
# A segment of a line, defined by two coordinates, a start and an end.
LineSegment = Tuple[Coord, Coord]
# From Shapely: (minx, miny, maxx, maxy)
Bounds = Tuple[float, float, float, float]


def create_polygon_from_stripe_lines_x_bounded(
        stripe_line_1: Line,
        stripe_line_2: Line,
        bounds: Bounds
) -> Polygon:
    if stripe_line_1[1][0] != stripe_line_2[1][0] and \
            stripe_line_1[1][1] != stripe_line_2[1][1]:
        raise ValueError('stripe_lines must be parallel')

    line_string_1 = create_line_string_from_stripe_line_x_bounded(
        stripe_line_1,
        bounds
    )
    line_string_2 = create_line_string_from_stripe_line_x_bounded(
        stripe_line_2,
        bounds
    )

    return Polygon([
        line_string_1.coords[0],
        line_string_1.coords[1],
        line_string_2.coords[1],
        line_string_2.coords[0]
    ])


def create_line_string_from_stripe_line_x_bounded(
        stripe_line: Line,
        bounds: Bounds
) -> LineString:
    # If the unit vector of the line is straight up or straight down, bound the
    # line to the bounds.
    if stripe_line[1][0] == 0:
        return LineString([
            (stripe_line[0][0], bounds[1]),
            (stripe_line[0][0], bounds[3])
        ])

    # The above if-statement asserts that the stripe_line must intersect the
    # bounds horizontally, therefore the output of the functions below will
    # never return `None`.
    start_point = line_intersection(stripe_line, ((bounds[0], 0), (0, 1)))
    end_point = line_intersection(stripe_line, ((bounds[2], 0), (0, 1)))

    return LineString([
        start_point,
        end_point
    ])
