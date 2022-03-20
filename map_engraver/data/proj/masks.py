from typing import Tuple, List

import math

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
    # Throw an error if an unknown projection is passed in.
    print(crs.coordinate_operation.method_name)
    if crs.coordinate_operation.method_name not in [
        'Orthographic',
        'Geostationary Satellite (Sweep X)',
        'Geostationary Satellite (Sweep Y)',
    ]:
        raise Exception(
            'projection method name not supported: ' +
            crs.coordinate_operation.method_name
        )

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
        # Stitch points together
        points = _split_points_along_anti_meridian(crs, points)[0]
        # Used to determine which hemisphere the origin is in.
        origin = transformer.transform(0, 0)
        # Extend the path by including points at the North or South Pole.
        points.extend([
            (_sign(origin[0]) * 90, _sign(points[-1][1]) * 180),
            (_sign(origin[0]) * 90, _sign(points[-1][1]) * -180),
        ])

        return MultiPolygon([Polygon(points)])
    else:
        point_groups = _split_points_along_anti_meridian(crs, points)
        return MultiPolygon(list(map(
            lambda point_group: Polygon(point_group),
            point_groups
        )))


def _sign(x: float) -> float:
    return math.copysign(1, x)


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
    min_r = 0
    if crs.coordinate_operation.method_name == 'Orthographic':
        # Speeds up binary search a bit
        min_r = min(
            crs.ellipsoid.semi_minor_metre,
            crs.ellipsoid.semi_major_metre
        ) * 0.9

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


def _binary_search_edge_wgs84(
        crs: CRS,
        valid_lat: float,
        invalid_lat: float,
        threshold=0.01,
) -> float:
    """

    :param crs:
    :param valid_lat:
    :param invalid_lat:
    :param threshold: Defaults to 0.01, since this level of precision usually
                      is the size of a neighbourhood.
                      See https://xkcd.com/2170/
    :return:
    """
    transformer = Transformer.from_proj(
        CRS.from_epsg(4326),
        crs
    )

    while abs(valid_lat - invalid_lat) > threshold:
        pivot_lat = (invalid_lat + valid_lat) / 2
        if (transformer.transform(pivot_lat, 180))[0] == float('inf'):
            invalid_lat = pivot_lat
        else:
            valid_lat = pivot_lat

    return valid_lat


def _split_points_along_anti_meridian(
        crs: CRS,
        points: List[Tuple[float, float]],
        threshold=0.01
) -> List[List[Tuple[float, float]]]:
    transformer = Transformer.from_proj(
        CRS.from_epsg(4326),
        crs
    )

    total_points = len(points)
    groups: List = []
    group: List[Tuple[float, float]] = []
    for i in range(len(points)):
        current_point = points[i]
        next_point = points[(i + 1) % total_points]

        group.append(current_point)

        if abs(current_point[1] - next_point[1]) > 90:
            longitude = _sign(points[i][1]) * 180
            anti_meridian_at_current_lat = transformer.transform(current_point[0], 180)
            anti_meridian_at_next_lat = transformer.transform(next_point[0], 180)
            if anti_meridian_at_current_lat[0] == float('inf') and \
                    anti_meridian_at_next_lat[0] == float('inf'):
                raise RuntimeError(
                    'The anti-meridian at between the latitudes %f and %f '
                    'could not be transformed with the projection. This is '
                    'unexpected. Please fix the algorithm!'
                )

            if anti_meridian_at_current_lat[0] == float('inf'):
                latitude = _binary_search_edge_wgs84(
                    crs,
                    next_point[0],  # Valid latitude
                    current_point[0],  # Invalid latitude
                    threshold
                )
            elif anti_meridian_at_next_lat[0] == float('inf'):
                latitude = _binary_search_edge_wgs84(
                    crs,
                    current_point[0],  # Valid latitude
                    next_point[0],  # Invalid latitude
                    threshold
                )
            else:
                latitude = next_point[0]

            if not math.isclose(current_point[1], longitude, abs_tol=0.0001):
                group.append((latitude, longitude))

            groups.append(group)

            group = []
            if not math.isclose(next_point[1], -longitude, abs_tol=0.0001):
                print('222', current_point[1], next_point[1])
                print('hmmm', next_point[1], -longitude)
                group.append((latitude, -longitude))

        if len(groups) != 0 and groups[0][0] == next_point:
            group.extend(groups[0])
            groups[0] = group
        elif i == total_points - 1:
            groups.append(group)


    return groups
