from typing import Tuple, List

import math

from pyproj import CRS, Transformer
from shapely.geometry import Polygon, MultiPolygon


def orthographic_mask(
        crs: CRS,
        resolution=64,
        threshold=1
) -> Polygon:
    # Throw an error if an unknown projection is passed in.
    if not _is_supported_projection_method(crs):
        raise Exception(
            'projection method name not supported: ' +
            crs.coordinate_operation.method_name
        )

    proj_to_wgs84 = Transformer.from_proj(
        crs,
        CRS.from_epsg(4326)
    )
    points = []
    for i in range(resolution * 4):
        angle = i * math.pi * 2 / (resolution * 4)
        radius = _binary_search_edge_crs(proj_to_wgs84, angle, threshold)
        position = (
            math.cos(angle) * radius,
            math.sin(angle) * radius
        )
        points.append(position)
    return Polygon(points)


def orthographic_mask_wgs84(
        crs: CRS,
        resolution=64,
        threshold=1
) -> MultiPolygon:
    """

    :param crs:
    :param resolution: Determines the number of segments used to approximate a
                       quarter circle around a point.
    :param threshold: The mask's edge precision, measured in units of the CRS.
    :return:
    """
    # Throw an error if an unknown projection is passed in.
    if not _is_supported_projection_method(crs):
        raise Exception(
            'projection method name not supported: ' +
            crs.coordinate_operation.method_name
        )

    proj_to_wgs84 = Transformer.from_proj(
        crs,
        CRS.from_epsg(4326)
    )
    wgs84_to_proj = Transformer.from_proj(
        CRS.from_epsg(4326),
        crs
    )
    points = []
    for i in range(resolution * 4):
        angle = i * math.pi * 2 / (resolution * 4)
        radius = _binary_search_edge_crs(proj_to_wgs84, angle, threshold)
        position = proj_to_wgs84.transform(
            math.cos(angle) * radius,
            math.sin(angle) * radius
        )
        points.append(position)

    if _covers_hemisphere(wgs84_to_proj):
        # Stitch points together
        points = _split_points_along_anti_meridian(wgs84_to_proj, points)[0]
        # Used to determine which hemisphere the origin is in.
        origin = proj_to_wgs84.transform(0, 0)
        # Extend the path by including points at the North or South Pole.
        points.extend([
            (_sign(origin[0]) * 90, _sign(points[-1][1]) * 180),
            (_sign(origin[0]) * 90, _sign(points[-1][1]) * -180),
        ])

        return MultiPolygon([Polygon(points)])
    else:
        point_groups = _split_points_along_anti_meridian(
            wgs84_to_proj,
            points
        )
        return MultiPolygon(list(map(
            lambda point_group: Polygon(point_group),
            point_groups
        )))


def _is_supported_projection_method(crs: CRS) -> bool:
    return crs.coordinate_operation.method_name in [
        'Orthographic',  # ortho
        'Geostationary Satellite (Sweep X)',  # geos
        'Geostationary Satellite (Sweep Y)',  # geos
        'Vertical Perspective',  # nsper
        'PROJ tpers',  # tpers
    ]


def _sign(x: float) -> float:
    return math.copysign(1, x)


def _covers_hemisphere(wgs84_to_proj: Transformer) -> bool:
    covers_northern = wgs84_to_proj.transform(90, 0)[0] != float('inf')
    covers_southern = wgs84_to_proj.transform(-90, 0)[0] != float('inf')

    # We don't really support projections like this, where the north and south
    # poles are visible at the same, but it is possible in orthographic
    # projections where the lat_0 is 0. For our purposes, we don't consider
    # this projection as covering both hemisphere; it merely touches it.
    if covers_northern and covers_southern:
        return False
    return covers_northern or covers_southern


def _binary_search_edge_crs(
        transformer: Transformer,
        angle: float,
        threshold=1
) -> float:
    min_r = 0
    crs = transformer.source_crs
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
        wgs84_to_proj: Transformer,
        valid_lat: float,
        invalid_lat: float,
        threshold=0.01,
) -> float:
    """

    :param wgs84_to_proj:
    :param valid_lat:
    :param invalid_lat:
    :param threshold: Defaults to 0.01, since this level of precision usually
                      is the size of a neighbourhood.
                      See https://xkcd.com/2170/
    :return:
    """

    while abs(valid_lat - invalid_lat) > threshold:
        pivot_lat = (invalid_lat + valid_lat) / 2
        if (wgs84_to_proj.transform(pivot_lat, 180))[0] == float('inf'):
            invalid_lat = pivot_lat
        else:
            valid_lat = pivot_lat

    return valid_lat


def _split_points_along_anti_meridian(
        wgs84_to_proj: Transformer,
        points: List[Tuple[float, float]],
        threshold=0.01
) -> List[List[Tuple[float, float]]]:
    total_points = len(points)
    groups: List = []
    group: List[Tuple[float, float]] = []
    for i in range(len(points)):
        current_point = points[i]
        next_point = points[(i + 1) % total_points]

        group.append(current_point)

        if abs(current_point[1] - next_point[1]) > 90:
            longitude = _sign(points[i][1]) * 180
            anti_meridian_at_current_lat = wgs84_to_proj.transform(
                current_point[0], 180
            )
            anti_meridian_at_next_lat = wgs84_to_proj.transform(
                next_point[0], 180
            )
            if anti_meridian_at_current_lat[0] == float('inf') and \
                    anti_meridian_at_next_lat[0] == float('inf'):
                raise RuntimeError(
                    'The anti-meridian at between the latitudes %f and %f '
                    'could not be transformed with the projection. This is '
                    'unexpected. Please fix the algorithm!'
                )

            if anti_meridian_at_current_lat[0] == float('inf'):
                latitude = _binary_search_edge_wgs84(
                    wgs84_to_proj,
                    next_point[0],  # Valid latitude
                    current_point[0],  # Invalid latitude
                    threshold
                )
            elif anti_meridian_at_next_lat[0] == float('inf'):
                latitude = _binary_search_edge_wgs84(
                    wgs84_to_proj,
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
                group.append((latitude, -longitude))

        if len(groups) != 0 and groups[0][0] == next_point:
            group.extend(groups[0])
            groups[0] = group
        elif i == total_points - 1:
            groups.append(group)

    return groups
