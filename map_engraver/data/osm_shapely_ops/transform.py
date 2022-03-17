from shapely import ops
from typing import TypeVar

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
        distortion_threshold=0.5  # Maximum distance that interpolated coordinates can be from the real coordinates.
) -> T:

    return geom


def transform_interpolated_wgs84_geodesic(
        func,
        geom: T,
        distortion_threshold=0.5  # Maximum distance that interpolated coordinates can be from the real coordinates.
) -> T:
    '''

    :param func:
    :param geom:
    :param distortion_threshold:
    :return:
    '''
    return geom
