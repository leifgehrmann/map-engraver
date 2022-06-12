import math
from shapely.geometry import Polygon, LineString, MultiPolygon

from typing import Tuple, Union, List, Iterator, Optional

from map_engraver.data.math.trig import line_intersection, \
    scalar_between_lines_origin_and_projected_point
from map_engraver.data.osm_shapely_ops.homogenize import geoms_to_multi_polygon

Vector = Tuple[float, float]
Coord = Tuple[float, float]
UnitVector = Tuple[float, float]
# A line, defined by two vectors, an origin, and direction.
Line = Tuple[Vector, Vector]
# A segment of a line, defined by two coordinates, a start and an end.
LineSegment = Tuple[Coord, Coord]
# From Shapely: (minx, miny, maxx, maxy)
Bounds = Tuple[float, float, float, float]


def create_polygons_from_stripe_data(
        geom: Union[Polygon, MultiPolygon],
        line: Line,
        stripe_widths: List[float]
) -> List[Optional[Union[Polygon, MultiPolygon]]]:
    perpendicular_line = _create_perpendicular_line(line, 0)
    offset_range = _calculate_stripe_range(geom.bounds, perpendicular_line)

    polygons_per_stripe = [[] for _ in range(len(stripe_widths))]
    geoms_per_stripe: List[Optional[Union[Polygon, MultiPolygon]]] = \
        [None for _ in range(len(stripe_widths))]

    start_stripe_info = None
    for end_stripe_info in _stripe_iterator(
            offset_range, stripe_widths, True
    ):
        if start_stripe_info is None:
            start_stripe_info = end_stripe_info
            continue

        start_stripe_offset = start_stripe_info[1]
        end_stripe_offset = end_stripe_info[1]
        start_line = _create_perpendicular_line(
            perpendicular_line, start_stripe_offset
        )
        end_line = _create_perpendicular_line(
            perpendicular_line, end_stripe_offset
        )
        polygon = create_polygon_from_stripe_lines_x_bounded(
            start_line,
            end_line,
            geom.bounds
        )

        stripe_index = start_stripe_info[0]
        polygons_per_stripe[stripe_index].append(polygon)

        start_stripe_info = end_stripe_info

    for (stripe_index, polygons_for_stripe) in enumerate(polygons_per_stripe):
        if len(polygons_for_stripe) == 0:
            continue
        stripe_multipolygon = MultiPolygon(polygons_for_stripe)

        intersected_geom = geom.intersection(stripe_multipolygon)
        intersected_geom = geoms_to_multi_polygon(intersected_geom)
        if intersected_geom.is_empty:
            geoms_per_stripe[stripe_index] = None
        else:
            geoms_per_stripe[stripe_index] = intersected_geom

    return geoms_per_stripe


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


def _calculate_stripe_range(
        bounds: Bounds,
        perpendicular_line: Line
) -> Tuple[float, float]:
    coords = _convert_bounds_to_coords(bounds)
    scalars = []
    for coord in coords:
        scalars.append(scalar_between_lines_origin_and_projected_point(
            perpendicular_line,
            coord
        ))
    return min(scalars), max(scalars)


def _stripe_iterator(
        stripe_range: Tuple[float, float],
        stripe_widths: List[float],
        include_outer_stripes: bool
) -> Iterator[Tuple[int, float]]:
    total_stripe_widths = sum(stripe_widths)
    min_stripe_range = math.floor(stripe_range[0] / total_stripe_widths)
    min_stripe_range *= total_stripe_widths
    stripe_offset = min_stripe_range
    stripe_index = 0
    while stripe_offset < stripe_range[1]:
        stripe_to_yield = stripe_index, stripe_offset

        stripe_offset += stripe_widths[stripe_index]
        stripe_index = (stripe_index + 1) % len(stripe_widths)

        # Don't yield a value if we haven't even reached a stripe that is
        # within the stripe range.
        if stripe_offset > stripe_range[0] or \
                (
                        stripe_to_yield[1] > stripe_range[0] and
                        include_outer_stripes
                ):
            yield stripe_to_yield

    if include_outer_stripes:
        yield stripe_index, stripe_offset


def _convert_bounds_to_coords(
        bounds: Bounds
) -> Tuple[Coord, Coord, Coord, Coord]:
    return (
        (bounds[0], bounds[1]),
        (bounds[2], bounds[1]),
        (bounds[2], bounds[3]),
        (bounds[0], bounds[3]),
    )


def _create_perpendicular_line(line: Line, origin_offset: float) -> Line:
    new_origin = (
        line[0][0] + line[1][0] * origin_offset,
        line[0][1] + line[1][1] * origin_offset,
    )
    new_direction_unit_vector = (
        -line[1][1],
        line[1][0]
    )
    return new_origin, new_direction_unit_vector
