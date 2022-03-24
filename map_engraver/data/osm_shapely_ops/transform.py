import math

from shapely import ops
from shapely.geometry import Polygon, MultiPolygon
from typing import TypeVar, Tuple, List

from map_engraver.data.osm_shapely.osm_line_string import OsmLineString
from map_engraver.data.osm_shapely.osm_point import OsmPoint
from map_engraver.data.osm_shapely.osm_polygon import OsmPolygon

T = TypeVar('T')


def transform(func, geom: T) -> T:
    new_geom = ops.transform(func, geom)
    if isinstance(geom, OsmLineString):
        new_geom = OsmLineString(new_geom)
        new_geom.osm_tags = geom.osm_tags
    elif isinstance(geom, OsmPoint):
        new_geom = OsmPoint(new_geom)
        new_geom.osm_tags = geom.osm_tags
    elif isinstance(geom, OsmPolygon):
        new_geom = OsmPolygon(new_geom)
        new_geom.osm_tags = geom.osm_tags
    else:
        raise RuntimeError('Unexpected geom type: ' + geom.__class__.__name__)
    return new_geom
    pass


def transform_interpolated_euclidean(
        func,
        geom: T,
        distortion_threshold=0.25
) -> T:
    """
    ...

    This function is generally only useful when displaying work maps. If
    geodesic distortion is not expected, use `transform()` instead.

    :param func:
    :param geom:
    :param distortion_threshold: Maximum distance that interpolated coordinates
                                 can be from the real coordinates.
    :return:
    """
    new_coords = []
    # Todo: Support line-strings
    if isinstance(geom, Polygon):
        # Todo: Support interiors
        for i in range(len(geom.exterior.coords) - 1):
            a = geom.exterior.coords[i]
            b = geom.exterior.coords[i + 1]
            interpolated_points = _transform_interpolated_euclidean_segment(
                func,
                a,
                b,
                distortion_threshold=distortion_threshold
            )
            new_coords.append(func(*a))
            new_coords.extend(interpolated_points)
        # Todo: Confirm that polygons have a return co-ordinate.
        new_coords.append(func(*geom.exterior.coords[-1]))
        return Polygon(new_coords)
    if isinstance(geom, MultiPolygon):
        new_geoms = []
        for sub_geom in geom.geoms:
            new_geoms.append(transform_interpolated_euclidean(
                func,
                sub_geom,
                distortion_threshold=distortion_threshold
            ))
        return MultiPolygon(new_geoms)
    return geom


def _transform_interpolated_euclidean_segment(
        func,
        a: Tuple[float, float],
        b: Tuple[float, float],
        distortion_threshold=0.25
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
    :param distortion_threshold:
    :return: A list of points between a and b that minimize the transformed
             distortion.
    """
    euclidean_mid_point = ((a[0]+b[0])/2, (a[1]+b[1])/2)
    a_proj = func(*a)
    b_proj = func(*b)
    euclidean_mid_point_proj = func(*euclidean_mid_point)

    # This is the mid-point that would be displayed if we did not use
    # euclidean interpolation.
    fake_mid_point_proj = ((a_proj[0]+b_proj[0])/2, (a_proj[1]+b_proj[1])/2)

    # Ideally this should not happen, but there will be edge cases (literally!)
    # where an interpolated point could dip in and out of a map. The shape
    # should ideally be clipped to avoid this from happening, using a mask that
    # contains no points outside the allowed projection.
    if euclidean_mid_point_proj[0] == float('inf'):
        return []

    distortion = math.sqrt(
        ((euclidean_mid_point_proj[0]-fake_mid_point_proj[0])**2) +
        ((euclidean_mid_point_proj[1]-fake_mid_point_proj[1])**2)
    )
    if distortion > distortion_threshold:
        left_points = _transform_interpolated_euclidean_segment(
            func,
            a,
            euclidean_mid_point,
            distortion_threshold=distortion_threshold
        )
        right_points = _transform_interpolated_euclidean_segment(
            func,
            euclidean_mid_point,
            b,
            distortion_threshold=distortion_threshold
        )
        new_points = left_points
        new_points.append(euclidean_mid_point_proj)
        new_points.extend(right_points)
        return new_points

    return []





def transform_interpolated_wgs84_geodesic(
        func,
        geom: T,
        distortion_threshold=0.5
) -> T:
    """
    :param func:
    :param geom:
    :param distortion_threshold: Maximum distance that interpolated coordinates
                                 can be from the real coordinates.
    :return:
    """
    return geom
