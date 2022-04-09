from shapely import ops
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString
from typing import TypeVar, Tuple, List

from map_engraver.data.math.trig import obtuse_angle

T = TypeVar('T')


def transform_interpolated_euclidean(
        func,
        geom: T,
        angular_distortion_threshold=1
) -> T:
    """
    Todo: provide a better description.

    Todo: This function might not result the right results if the transformed
     line-segment's midpoint happens to be co-linear... Probably should fix
     this later.

    This function is generally only useful when displaying work maps. If
    geodesic distortion is not expected, use `transform()` instead.

    :param func:
    :param geom:
    :param angular_distortion_threshold: The maximum obtuse angle that can
                                         exist between two interpolated
                                         line-segments.
    :return:
    """
    if isinstance(geom, LineString):
        return LineString(_transform_interpolated_euclidean_coords(
            func,
            geom.coords,
            angular_distortion_threshold=angular_distortion_threshold
        ))
    elif isinstance(geom, Polygon):
        new_exterior = _transform_interpolated_euclidean_coords(
            func,
            geom.exterior.coords,
            angular_distortion_threshold=angular_distortion_threshold
        )
        new_interiors = []
        for interior in geom.interiors:
            new_interiors.append(_transform_interpolated_euclidean_coords(
                func,
                interior.coords,
                angular_distortion_threshold=angular_distortion_threshold
            ))
        return Polygon(new_exterior, new_interiors)
    elif isinstance(geom, MultiLineString):
        new_line_strings = []
        for line_string in geom.geoms:
            new_line_strings.append(transform_interpolated_euclidean(
                func,
                line_string,
                angular_distortion_threshold=angular_distortion_threshold
            ))
        return MultiLineString(new_line_strings)
    elif isinstance(geom, MultiPolygon):
        new_polygons = []
        for polygon in geom.geoms:
            new_polygons.append(transform_interpolated_euclidean(
                func,
                polygon,
                angular_distortion_threshold=angular_distortion_threshold
            ))
        return MultiPolygon(new_polygons)
    return ops.transform(func, geom)


def _transform_interpolated_euclidean_coords(
        func,
        coords: List[Tuple[float, float]],
        angular_distortion_threshold
) -> List[Tuple[float, float]]:
    if len(coords) == 0:
        return []
    new_coords = []
    for i in range(len(coords) - 1):
        a = coords[i]
        b = coords[i + 1]
        interpolated_points = _transform_interpolated_euclidean_segment(
            func,
            a,
            b,
            angular_distortion_threshold=angular_distortion_threshold
        )
        new_coords.append(func(*a))
        new_coords.extend(interpolated_points)

    new_coords.append(func(*coords[-1]))

    return new_coords


def _transform_interpolated_euclidean_segment(
        func,
        a: Tuple[float, float],
        b: Tuple[float, float],
        angular_distortion_threshold
) -> List[Tuple[float, float]]:
    """
    This function interpolates points between two points, in a way to minimizes
    the overall distortion of a line-segment by the transformation function.

    For example, The United States of America has a border at the 49 degrees
    north. Projecting the United States onto a globe, the line should appear
    curved, as the line segment is not a geodesic line. However, naively
    rendering the line segment in a simple vector graphics tool will not
    display the curved points. This function will return the set of points
    along the that border to preserve the curved nature when rendering the
    vector shape.

    :param func: The transformation function.
    :param a: The starting point of a line segment.
    :param b: The starting point of a line segment.
    :param angular_distortion_threshold:
    :return: A list of points between a and b that minimize the transformed
             distortion.
    """
    euclidean_mid_point = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    a_proj = func(*a)
    b_proj = func(*b)
    euclidean_mid_point_proj = func(*euclidean_mid_point)

    # Ideally this should not happen, but there will be edge cases (literally!)
    # where an interpolated point could dip in and out of a map. The shape
    # should ideally be clipped to avoid this from happening, using a mask that
    # contains no points outside the allowed projection.
    if euclidean_mid_point_proj[0] == float('inf'):
        return []

    angular_distortion = obtuse_angle(a_proj, b_proj, euclidean_mid_point_proj)
    is_distorted = (
            angular_distortion != float('inf') and
            angular_distortion_threshold < 180 - angular_distortion
    )

    if is_distorted:
        left_points = _transform_interpolated_euclidean_segment(
            func,
            a,
            euclidean_mid_point,
            angular_distortion_threshold=angular_distortion_threshold
        )
        right_points = _transform_interpolated_euclidean_segment(
            func,
            euclidean_mid_point,
            b,
            angular_distortion_threshold=angular_distortion_threshold
        )
        new_points = left_points
        new_points.append(euclidean_mid_point_proj)
        new_points.extend(right_points)
        return new_points

    return []
