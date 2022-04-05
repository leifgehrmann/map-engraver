from math import sqrt, sin, cos, atan2, copysign, acos, pi

from shapely.geometry import LineString, MultiLineString
from typing import Union, Tuple, List, Optional

from map_engraver.data.math.trig import obtuse_angle

Coord = Tuple[float, float]  # (latitude, longitude)
Vector = Tuple[float, float]
LineSegments = List[Coord]


def interpolate_geodesic(
        geom: Union[LineString, MultiLineString],
        angular_distortion_threshold=1
) -> MultiLineString:
    """
    Adds additional line-segments to an existing LineString shapely object so
    that each line-segment follows the great-circle path (i.e. the shortest
    distance between two points on a sphere), rather than a euclidean path.

    A common use-case is to convert a flight-path between two cities on a
    globe.

    If the shortest-distance between two points happens to cross the poles, the
    LineStrings may be split and return a MultiLineString.

    The algorithm only applies to LineStrings and MultiLineStrings and not for
    Polygons and MultiPolygons because for a polygon it is easily possible for
    line-segments to overlap by transforming each individual line-segment, thus
    producing an invalid polygon. If such functionality is desired, convert the
    polygon's coordinates to a LineString, and then convert it back.

    :param geom: A line-string or multi-line-string shapely object with WGS 84
                 coordinates.
    :param angular_distortion_threshold: The maximum obtuse angle that can
                                         exist between two interpolated
                                         line-segments.
    :return: A collection of line-strings with additional
    """
    if isinstance(geom, LineString):
        return MultiLineString(_interpolate_geodesic_line_string(
            geom,
            angular_distortion_threshold=angular_distortion_threshold
        ))
    elif isinstance(geom, MultiLineString):
        new_line_strings = []
        for line_string in geom.geoms:
            new_line_strings.extend(_interpolate_geodesic_line_string(
                line_string,
                angular_distortion_threshold=angular_distortion_threshold
            ))
        return MultiLineString(new_line_strings)
    raise RuntimeError('Unexpected geom type: ' + geom.__class__.__name__)


def _interpolate_geodesic_line_string(
        line_string: LineString,
        angular_distortion_threshold: float
) -> List[LineString]:
    new_line_strings = []
    new_line_string_coords = []
    for i in range(len(line_string.coords) - 1):
        a = line_string.coords[i]
        b = line_string.coords[i + 1]
        interpolated_coords, split_coords = _interpolate_geodesic_line_segment(
            a,
            b,
            angular_distortion_threshold=angular_distortion_threshold
        )
        new_line_string_coords.extend(interpolated_coords)
        if split_coords is not None:
            if len(new_line_string_coords) > 1:
                new_line_strings.append(LineString(new_line_string_coords))
            new_line_string_coords = split_coords

    # Append the last coord to the end of the line-segments
    new_line_string_coords.append(line_string.coords[-1])

    # Finalize the
    if len(new_line_string_coords) > 1:
        new_line_strings.append(LineString(new_line_string_coords))

    return new_line_strings


def _sign(x: float) -> float:
    return copysign(1, x)


def _interpolate_geodesic_line_segment(
        a_wgs84: Coord,
        b_wgs84: Coord,
        angular_distortion_threshold: float
) -> Tuple[LineSegments, Optional[LineSegments]]:
    """
    :param a_wgs84:
    :param b_wgs84:
    :param angular_distortion_threshold:
    :return:
    """
    # If the great-circle path intersects the poles, we want to split the line
    # segment in two. One segment that goes straight to the pole, and another
    # segment that starts from the pole. The function does not return the
    # b-coordinate as that will be appended by the interpolate_geodesic
    # algorithm.
    if (a_wgs84[1] + 360) % 360 == (b_wgs84[1] + 180 + 360) % 360:
        # If the point is starting from a pole we want to split the
        # line-segments at this point.
        if abs(a_wgs84[0]) == 90:
            return [a_wgs84], [(90 * _sign(a_wgs84[0]), b_wgs84[1])]

        # Conversely, if the point ends at a pole, we want to split the
        # line-segments at the point it reaches the pole.
        if abs(b_wgs84[0]) == 90:
            return [a_wgs84, (90 * _sign(b_wgs84[0]), a_wgs84[1])], []

        # If none of the coordinates are at the pole we want a line-segment
        # that travels to the pole, then in a new line string, a coordinate
        # starts from the pole.
        lat_direction = 1 if a_wgs84[0] > -b_wgs84[0] else -1
        return [
                   a_wgs84,
                   (90 * lat_direction, a_wgs84[1])
               ], [(90 * lat_direction, b_wgs84[1])]

    # If the coordinate is on the same longitude, the shortest path will
    # always be a vertical line, so we can skip interpolation.
    if a_wgs84[1] == b_wgs84[1]:
        return [a_wgs84], None

    # Does the shortest path cross the anti-meridian? (i.e. are the longitudes
    # closer via the anti-meridian)
    if abs(a_wgs84[1] - b_wgs84[1]) > 180:
        if a_wgs84[1] > b_wgs84[1]:
            # `a_wgs84` is in the eastern hemisphere.
            eastern_coord = a_wgs84
            western_coord = b_wgs84
        else:
            # `a_wgs84` is in the western hemisphere.
            eastern_coord = b_wgs84
            western_coord = a_wgs84
        anti_meridian_lat = _locate_anti_meridian_latitude(
            eastern_coord,
            western_coord
        )
        a_anti_meridian_intersection = (
            anti_meridian_lat,
            180 * _sign(a_wgs84[1])
        )
        b_anti_meridian_intersection = (
            anti_meridian_lat,
            180 * _sign(b_wgs84[1])
        )

        a_to_meridian = _interpolate_geodesic_coords(
            a_wgs84,
            a_anti_meridian_intersection,
            angular_distortion_threshold
        )
        a_to_meridian.append(a_anti_meridian_intersection)
        meridian_to_b = _interpolate_geodesic_coords(
            b_anti_meridian_intersection,
            b_wgs84,
            angular_distortion_threshold
        )
        return a_to_meridian, meridian_to_b

    return _interpolate_geodesic_coords(
        a_wgs84,
        b_wgs84,
        angular_distortion_threshold
    ), None


def _locate_anti_meridian_latitude(
        a_wgs84: Coord,
        b_wgs84: Coord,
        longitude_threshold=0.0001
) -> float:
    """
    :param a_wgs84: A WGS 84 coordinate on the eastern hemisphere.
    :param b_wgs84: A WGS 84 coordinate on the western hemisphere.
    :param longitude_threshold: How precise the value should be to pin-point
                                the 180° longitude. The default is 0.0001, as
                                according to [xkcd](https://www.xkcd.com/2170/)
                                four decimal places will be precise enough to
                                pin-point a house.
    :return:
    """
    mid_point_wgs84 = _interpolate_geodesic_coords_at_mid_point(
        a_wgs84,
        b_wgs84
    )
    if abs(abs(mid_point_wgs84[1]) - 180) < longitude_threshold:
        return mid_point_wgs84[0]

    # Mid-point is in the eastern hemisphere.
    if mid_point_wgs84[1] > a_wgs84[1]:
        return _locate_anti_meridian_latitude(
            mid_point_wgs84,
            b_wgs84,
            longitude_threshold=longitude_threshold
        )

    # Otherwise, the mid-point is in the western hemisphere.
    return _locate_anti_meridian_latitude(
        a_wgs84,
        mid_point_wgs84,
        longitude_threshold=longitude_threshold
    )


def _interpolate_geodesic_coords(
        a_wgs84: Coord,
        b_wgs84: Coord,
        angular_distortion_threshold
) -> List[Coord]:
    """
    :param a_wgs84:
    :param b_wgs84:
    :param angular_distortion_threshold:
    :return:
    """
    mid_point_wgs84 = _interpolate_geodesic_coords_at_mid_point(
        a_wgs84,
        b_wgs84,
    )

    # If the coordinates are opposite sides of the latitude, we want to split
    # the segments up more, since an S curve could return results prematurely
    # since the angular distortion is less at the equator. But, to avoid
    # infinite loops, we make an exception for coordinates that are 10° degrees
    # apart, since an s-curve won't happen at small angles.
    has_s_curve = _sign(a_wgs84[0]) != _sign(a_wgs84[1])
    far_apart = abs(a_wgs84[0] - b_wgs84[0]) > 10

    angular_distortion = obtuse_angle(a_wgs84, b_wgs84, mid_point_wgs84)

    is_distorted = (
            angular_distortion != float('inf') and
            angular_distortion_threshold < 180 - angular_distortion
    )

    should_split = (has_s_curve and far_apart) or is_distorted

    if not should_split:
        return [a_wgs84]

    new_points = []
    # Left split
    new_points.extend(_interpolate_geodesic_coords(
        a_wgs84,
        mid_point_wgs84,
        angular_distortion_threshold
    ))
    # Right split
    new_points.extend(_interpolate_geodesic_coords(
        mid_point_wgs84,
        b_wgs84,
        angular_distortion_threshold
    ))
    return new_points


def _interpolate_geodesic_coords_at_mid_point(p1: Coord, p2: Coord):
    """
    :param p1: The starting coordinate, in degrees.
    :param p2: The end coordinate, in degrees.
    :return: The coordinate half-way between the start and end, in degrees.
    """
    # Edge case: If the coordinates are antipodal at the North/South Pole, it
    # is ambiguous what the mid-point between these two coordinates is.
    # Normally this isn't a problem for any other antipodal coordinate on the
    # globe, but for the North/South Poles, it will cause the interpolator to
    # draw a non-geodesic line segment. For example: (90, 20) -> (-90, -20)
    # will result in (90, 0), which is the mid_point, but rendering the line
    # segment on a map will cause the line segment to be warped!
    # To solve this, we return a mid-point that shares the exact same longitude
    # as the starting coordinate.
    if abs(p1[0]) == 90 and abs(p2[0]) == 90 and p1[0] == -p2[0]:
        return 0, p1[1]

    p1 = p1[0] / 180 * pi, p1[1] / 180 * pi
    p2 = p2[0] / 180 * pi, p2[1] / 180 * pi
    delta = haversine(p1, p2)
    r = sin(0.5 * delta) / sin(delta)
    x = r * cos(p1[0]) * cos(p1[1]) + r * cos(p2[0]) * cos(p2[1])
    y = r * cos(p1[0]) * sin(p1[1]) + r * cos(p2[0]) * sin(p2[1])
    z = r * sin(p1[0]) + r * sin(p2[0])
    altitude = atan2(z, sqrt(x * x + y * y))
    azimuth = atan2(y, x)
    return altitude * 180 / pi, azimuth * 180 / pi


def haversine(p1: Coord, p2: Coord) -> float:
    """
    :param p1: The starting coordinate, in radians.
    :param p2: The end coordinate, in radians.
    :return: The distance between `p1` and `p2` in radians.
    """
    d = p2[0] - p1[0], p2[1] - p1[1]
    a = sin(d[0] / 2) * sin(d[0] / 2) + \
        cos(p1[0]) * cos(p2[0]) * sin(d[1] / 2) * sin(d[1] / 2)
    return 2 * atan2(sqrt(a), sqrt((1 - a)))
