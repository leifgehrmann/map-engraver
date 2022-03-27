import math

from pyproj import CRS, Transformer
from shapely.geometry import LineString, MultiLineString
from typing import Union, Tuple, List, Optional

Coords = Tuple[float, float]  # (latitude, longitude)
Vector = Tuple[float, float]
LineSegments = List[Coords]


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

    If the shortest-distance between two points happens to cross the poles or
    the Todo

    The algorithm only applies to LineStrings and MultiLineStrings because for
    a polygon it is easily possible for line-segments to overlap by
    transforming each individual line-segment, thus producing an invalid
    polygon.

    :param geom: A line-string or multi-line-string shapely object with WGS 84
                 coordinates.
    :param angular_distortion_threshold: Maximum distance in meters thatinterpolated
                                 coordinates can be from the real coordinates.
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
            new_line_strings.append(LineString(new_line_string_coords))
            new_line_string_coords = split_coords

    # Append the last coord to the end of the line-segments
    new_line_string_coords.append(line_string.coords[-1])

    # Finalize the
    new_line_strings.append(LineString(new_line_string_coords))

    return new_line_strings


def _sign(x: float) -> float:
    return math.copysign(1, x)


def _interpolate_geodesic_line_segment(
        a_wgs84: Coords,
        b_wgs84: Coords,
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
    if a_wgs84[1] == -b_wgs84[1]:
        print('crossing poles!')
        if abs(a_wgs84[0]) == 90 or abs(b_wgs84[0]) == 90:
            return [a_wgs84, b_wgs84], None
        # Are we traversing up or down the globe.
        lat_direction = 1 if a_wgs84[0] > -b_wgs84[0] else -1

        return [
                   a_wgs84,
                   (90 * lat_direction, a_wgs84[1])
               ], [(90 * lat_direction, b_wgs84[1])]

    # Gnomonic projections can be used to find the great circle distances
    # because the map projection displays all great circles as straight lines.
    # This means the straight line between a and b is equivalent to the great
    # circle path.
    gnomonic_proj = CRS.from_proj4('+proj=stere +lat_0=%f +lon_0=%f +lat_ts=10' % a_wgs84)
    wgs84_to_gnomonic = Transformer.from_proj(
        CRS.from_epsg(4326),
        gnomonic_proj
    )
    gnomonic_to_wgs84 = Transformer.from_proj(
        gnomonic_proj,
        CRS.from_epsg(4326)
    )
    # Our gnomonic projection uses `a_wgs84` as the origin.
    a_gnomonic = wgs84_to_gnomonic.transform(*a_wgs84)
    b_gnomonic = wgs84_to_gnomonic.transform(*b_wgs84)
    print('a,b, wgs84', a_wgs84, b_wgs84)
    print('a,b, gnomonic', a_gnomonic, b_gnomonic)

    # Does the shorted path cross the anti-meridian (i.e. are the longitudes
    # closer via the anti-meridian)
    if abs(a_wgs84[1] - b_wgs84[1]) > 180:
        print('crossed the anti-meridian')
        if a_wgs84[1] > b_wgs84[1]:
            # `a_wgs84` is in the eastern hemisphere.
            eastern_gnom_coord = a_gnomonic
            western_gnom_coord = b_gnomonic
        else:
            # `a_wgs84` is in the western hemisphere.
            eastern_gnom_coord = b_gnomonic
            western_gnom_coord = a_gnomonic
        anti_meridian_lat = _locate_anti_meridian_latitude(
            eastern_gnom_coord,
            western_gnom_coord,
            gnomonic_to_wgs84
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
            a_gnomonic,
            a_anti_meridian_intersection,
            wgs84_to_gnomonic.transform(*a_anti_meridian_intersection),
            gnomonic_to_wgs84,
            angular_distortion_threshold
        )
        a_to_meridian.append(a_anti_meridian_intersection)
        meridian_to_b = _interpolate_geodesic_coords(
            b_anti_meridian_intersection,
            wgs84_to_gnomonic.transform(*b_anti_meridian_intersection),
            b_wgs84,
            b_gnomonic,
            gnomonic_to_wgs84,
            angular_distortion_threshold
        )
        return a_to_meridian, meridian_to_b

    return _interpolate_geodesic_coords(
        a_wgs84,
        a_gnomonic,
        b_wgs84,
        b_gnomonic,
        gnomonic_to_wgs84,
        angular_distortion_threshold
    ), None


def _locate_anti_meridian_latitude(
        a_gnomonic: Coords,
        b_gnomonic: Coords,
        gnomonic_to_wgs84: Transformer,
        longitude_threshold=0.0001
) -> float:
    """
    :param a_gnomonic: A coordinate in the gnomonic projection that corresponds
                       to a coordinate on the eastern hemisphere in the WGS84
                       projection.
    :param b_gnomonic: A coordinate in the gnomonic projection that corresponds
                       to a coordinate on the western hemisphere in the WGS84
                       projection.
    :param gnomonic_to_wgs84: A transformation function that
    :param longitude_threshold: How precise the value should be to pin-point
                                the 180° longitude. The default is 0.0001, as
                                according to [xkcd](https://www.xkcd.com/2170/)
                                four decimal places will be precise enough to
                                pin-point a house.
    :return:
    """
    mid_point_gnomonic = _mid_point(a_gnomonic, b_gnomonic)
    mid_point_wgs84 = gnomonic_to_wgs84.transform(*mid_point_gnomonic)
    print(mid_point_wgs84)
    if abs(mid_point_wgs84[1]) - 180 < longitude_threshold:
        return -mid_point_wgs84[0]
    if mid_point_wgs84[1] > a_gnomonic[1]:  # Mid-point is in the eastern hemisphere.
        return _locate_anti_meridian_latitude(
            mid_point_gnomonic,
            b_gnomonic,
            gnomonic_to_wgs84,
            longitude_threshold=longitude_threshold
        )
    # Otherwise, the mid-point is in the western hemisphere.
    return _locate_anti_meridian_latitude(
        a_gnomonic,
        mid_point_gnomonic,
        gnomonic_to_wgs84,
        longitude_threshold=longitude_threshold
    )


def _interpolate_geodesic_coords(
        a_wgs84: Coords,
        a_gnomonic: Coords,
        b_wgs84: Coords,
        b_gnomonic: Coords,
        gnomonic_to_wgs84: Transformer,
        angular_distortion_threshold
) -> List[Coords]:
    """
    :param a_wgs84:
    :param a_gnomonic:
    :param b_wgs84:
    :param b_gnomonic:
    :param gnomonic_to_wgs84:
    :param angular_distortion_threshold:
    :return:
    """
    mid_point_gnomonic = _mid_point(a_gnomonic, b_gnomonic)
    mid_point_wgs84 = gnomonic_to_wgs84.transform(*mid_point_gnomonic)

    # If the coordinates are opposite sides of the latitude, we want to split
    # the segments up more, since an S curve could return results prematurely
    # since the angular distortion is less at the equator. But, to avoid
    # infinite loops, we make an exception for coordinates that are 10° degrees
    # apart, since an s-curve won't happen at small angles.
    has_s_curve = _sign(a_wgs84[0]) != _sign(a_wgs84[1])
    far_apart = abs(a_wgs84[0] - b_wgs84[0]) > 10

    angular_distortion = _obtuse_angle(a_wgs84, b_wgs84, mid_point_wgs84)
    is_distorted = angular_distortion_threshold < 180 - angular_distortion

    should_split = (has_s_curve and far_apart) or is_distorted
    print(a_wgs84, b_wgs84, should_split, angular_distortion)

    if not should_split:
        return [a_wgs84]

    new_points = []
    # Left split
    new_points.extend(_interpolate_geodesic_coords(
        a_wgs84,
        a_gnomonic,
        mid_point_wgs84,
        mid_point_gnomonic,
        gnomonic_to_wgs84,
        angular_distortion_threshold
    ))
    # Right split
    new_points.extend(_interpolate_geodesic_coords(
        mid_point_wgs84,
        mid_point_gnomonic,
        b_wgs84,
        b_gnomonic,
        gnomonic_to_wgs84,
        angular_distortion_threshold
    ))
    return new_points


def _mid_point(a: Coords, b: Coords) -> Coords:
    return (
        (a[0] + b[0]) / 2,
        (a[1] + b[1]) / 2
    )


def _diff(a: Coords, b: Coords) -> Coords:
    return (
        (b[0] - a[0]),
        (b[1] - a[1])
    )


def _magnitude(v: Vector) -> float:
    return math.sqrt(v[0] * v[0] + v[1] * v[1])


def _obtuse_angle(a: Coords, b: Coords, c: Coords):
    """
    Given all three coordinates of a triangle, this function returns the
    angle between `ca` and `cb`.

    :param a:
    :param b:
    :param c:
    :return:
    """
    ca = _diff(c, a)
    cb = _diff(c, b)
    ca_dot_bc = ca[0] * cb[0] + ca[1] * cb[1]
    angle_radians = math.acos(ca_dot_bc / (_magnitude(ca) * _magnitude(cb)))
    return angle_radians / math.pi * 180
