from typing import Tuple, List

import math

from pyproj import CRS, Transformer
from shapely.geometry import Polygon, MultiPolygon, box


def is_supported_azimuthal_projection(crs: CRS) -> bool:
    return crs.coordinate_operation.method_name in [
        'Orthographic',  # ortho
        'Geostationary Satellite (Sweep X)',  # geos
        'Geostationary Satellite (Sweep Y)',  # geos
        'Vertical Perspective',  # nsper
        'PROJ tpers',  # tpers
    ]


def azimuthal_mask(
        crs: CRS,
        resolution=64,
        threshold=1
) -> Polygon:
    """
    Generates a polygon that represents the shape of the `crs`.

    Points that exist within the polygon are points that can be mapped from the
    `crs` to the WGS 84 projection. Any point that is outside cannot be mapped
    between the `crs` and the WGS 84 projection.

    For example, with an orthographic projection, this function can be used as
    an easy way to create a polygon outlines the ocean of the globe.

    :param crs: The coordinate reference system to create a mask for.
    :param resolution: The number of points to approximate 1/4th of the mask.
                       In other words, 1 will return a polygon with 4
                       coordinates, and 64 will return a polygon with 256
                       points.
    :param threshold: The distance (measured in the `crs`'s units) between the
                      polygon's coordinates being from the actual boundary of
                      the `crs's` domain.
    :return: A polygon that approximates the `crs`'s domain in the `crs`'s own
             projection.
    """
    # Throw an error if an unknown projection is passed in.
    if not is_supported_azimuthal_projection(crs):
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


def azimuthal_mask_wgs84(
        crs: CRS,
        resolution=64,
        threshold=1
) -> MultiPolygon:
    """
    Generates a polygon that represents the shape of the `crs` in the WGS 84
    projection system.

    Points that exist within the polygon are points that can be mapped from the
    WGS 84 projection to the `crs`. Any point that is outside cannot be mapped
    between the `crs` and the WGS 84 projection.

    For example, with an orthographic projection, this function can be used as
    an easy way to clip a global polygon (like the world's coastlines) to fit
    within the actual orthographic projection.

    Todo: It is known that this algorithm isn't exactly full-proof.
    For example, +proj=ortho +lat_0=20 is known to produce some invalid edges.
    These are very rare edge cases, which we're ignoring for now, but we might
    need a better solution for later. One known solution is to actually make
    the whole mask consist of right angles, but this looks ugly when rendered.
    We could make this an optional argument if projections are still causing
    issues.

    :param crs: The coordinate reference system to create a mask for.
    :param resolution: The number of points to approximate 1/4th of the mask.
                       In other words, 1 will return a polygon with at least 4
                       coordinates, and 64 will return a polygon with at least
                       256 points.
    :param threshold: The distance (measured in the `crs`'s units) between the
                      polygon's coordinates being from the actual boundary of
                      the `crs's` domain.
    :return: A polygon that approximates the `crs`'s domain in the WGS 84
             projection.
    """
    # Throw an error if an unknown projection is passed in.
    if not is_supported_azimuthal_projection(crs):
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

        # If one of the positions is really close to the anti-meridian, but not
        # because of floating point errors, just set it to 180/-180.
        touches_anti_meridian = math.isclose(
            position[1],
            180 * _sign(position[1]),
            abs_tol=0.000000001
        ) or position[1] > 180 or position[1] < -180
        if touches_anti_meridian:
            position = (position[0], 180 * _sign(position[1]))

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

        return MultiPolygon([_trim_polygon(crs, Polygon(points))])
    else:
        point_groups = _split_points_along_anti_meridian(
            wgs84_to_proj,
            points
        )
        return MultiPolygon(list(map(
            lambda point_group: _trim_polygon(crs, Polygon(point_group)),
            point_groups
        )))


def _sign(x: float) -> float:
    return math.copysign(1, x)


def _covers_hemisphere(wgs84_to_proj: Transformer) -> bool:
    covers_northern = wgs84_to_proj.transform(90, 0)[0] != float('inf')
    covers_southern = wgs84_to_proj.transform(-90, 0)[0] != float('inf')

    # We don't really support projections like this, where the north and south
    # poles are visible at the same, but it is possible in azimuthal
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
                error = (
                    'The anti-meridian at between the latitudes ' +
                    "%f and %f " % (current_point[0], next_point[0]) +
                    'could not be transformed with the projection. This is ' +
                    'unexpected. Please fix the algorithm!'
                )
                raise RuntimeError(error)

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


def _trim_polygon(crs: CRS, polygon: Polygon) -> Polygon:
    """
    Remove coordinates from the polygon can cannot be interpolated easily but
    simply cutting out a box between the coordinates.

    :param crs: The coordinate reference system to verify.
    :param polygon: The polygon to cut.
    :return: A new polygon.
    """
    wgs84_to_proj = Transformer.from_proj(
        CRS.from_epsg(4326),
        crs
    )
    new_polygon = Polygon(polygon)
    for i in range(len(polygon.exterior.coords) - 1):
        a = polygon.exterior.coords[i]
        b = polygon.exterior.coords[i + 1]
        if a[0] == b[0] or a[1] == b[1]:
            continue

        # We want to preserve diagonals as much as possible, so we only cut off
        # pieces if the mid-point for two coordinates cannot be projected. But
        # this is known to produce false positives! So this might be removed.
        mid_point = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if wgs84_to_proj.transform(*mid_point)[0] != float('inf'):
            continue

        boxed_coordinates = _box_coordinates(a, b)
        new_polygon = new_polygon.difference(boxed_coordinates)
    return new_polygon


def _box_coordinates(a: Tuple[float, float], b: Tuple[float, float]):
    return box(
        min(a[0], b[0]),
        min(a[1], b[1]),
        max(a[0], b[0]),
        max(a[1], b[1]),
    )
