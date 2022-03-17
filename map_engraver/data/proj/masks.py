from pyproj.enums import TransformDirection
from typing import Tuple, List

import math
from operator import itemgetter

from pyproj import CRS, Transformer
from shapely.geometry import Polygon, MultiPolygon


def orthographic_mask(crs: CRS, resolution=64, threshold=1) -> MultiPolygon:
    """

    :param crs:
    :param resolution: Determines the number of segments used to approximate a
                       quarter circle around a point.
    :param threshold: The mask's edge precision, measured in units of the CRS.
    :return:
    """
    # Todo: throw an error if an unknown projection is passed in.
    print(crs.coordinate_operation.method_name)

    transformer = Transformer.from_proj(
        crs,
        CRS.from_epsg(4326)
    )
    points = []
    for i in range(resolution * 4):
        angle = i * math.pi * 2 / (resolution * 4)
        radius = _binary_search_edge_crs(crs, angle, threshold)
        position = transformer.transform(
            math.cos(angle) * radius,
            math.sin(angle) * radius
        )
        points.append(position)

    print('Covers Hemisphere:', _covers_hemisphere(points))

    if _covers_hemisphere(points):
        # Sort points by longitude
        points = list(sorted(points, key=itemgetter(1)))
        # Todo: Def
        origin = transformer.transform(0, 0)

        def sign(x: float) -> float:
            return math.copysign(1, x)

        anti_meridian_lat = _binary_search_edge_wgs84(crs)
        # Extend the path by including points at the North or South Pole.
        points.extend([
            (anti_meridian_lat, 180),
            (sign(origin[0]) * 90, 180),
            (sign(origin[0]) * 90, -180),
            (anti_meridian_lat, -180),
            points[0],
        ])

        # debug
        for point in points:
            print(point, 'a')

        return MultiPolygon([Polygon(points)])
    else:
        # Todo: Make sure if the mask crosses the anti-meridian that we ensure
        # we return a multi-polygon.
        for point in points:
            print(point, 'a')

    return MultiPolygon([Polygon(points)])


def _covers_hemisphere(points: List[Tuple[float, float]]) -> bool:
    # Returns true if the coordinate sequence's longitude starts going in the
    # reverse direction for more than a quarter of the sequence.
    # This is used to determine whether the projected edge is covers the whole
    # hemisphere.
    segments_increasing = 0
    segments_decreasing = 0
    total_points = len(points)
    for i in range(len(points)):
        if points[i][1] < points[(i + 1) % total_points][1]:
            segments_increasing += 1
        else:
            segments_decreasing += 1

    print('hemisphere check', total_points, segments_decreasing, segments_increasing)
    return 4 > min(segments_increasing, segments_decreasing)


def _binary_search_edge_crs(crs: CRS, angle: float, threshold=1) -> float:
    transformer = Transformer.from_proj(
        crs,
        CRS.from_epsg(4326)
    )
    # Todo:
    # If ortho:
    min_r = min(crs.ellipsoid.semi_minor_metre, crs.ellipsoid.semi_major_metre) * 0.9
    # If geos:
    min_r = 0

    max_r = max(crs.ellipsoid.semi_minor_metre, crs.ellipsoid.semi_major_metre)
    while max_r - min_r > threshold:
        pivot_r = (min_r + max_r) / 2
        x = math.cos(angle) * pivot_r
        y = math.sin(angle) * pivot_r
        if (transformer.transform(x, y))[0] == float('inf'):
            max_r = pivot_r
        else:
            min_r = pivot_r

    return min_r


def _binary_search_edge_wgs84(crs: CRS, threshold=0.000001) -> float:
    transformer = Transformer.from_proj(
        CRS.from_epsg(4326),
        crs
    )

    origin = transformer.transform(0, 0, direction=TransformDirection.INVERSE)

    def sign(x: float) -> float:
        return math.copysign(1, x)

    valid_lat = sign(origin[0]) * 90
    invalid_lat = -valid_lat
    while abs(valid_lat - invalid_lat) > threshold:
        pivot_lat = (invalid_lat + valid_lat) / 2
        print(invalid_lat, valid_lat, invalid_lat - invalid_lat, threshold)
        if (transformer.transform(pivot_lat, 180))[0] == float('inf'):
            invalid_lat = pivot_lat
        else:
            valid_lat = pivot_lat

    return valid_lat
