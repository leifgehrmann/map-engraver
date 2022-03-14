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

def transform_clipped(
        func,
        geom: T,
        clip_threshold=0.5, # Minimum distance from the edge a projection clip can occur.
        distortion_threshold=0.5, # Maximum distance that interpolated coordinates can be from the real coordinates.
        gap_threshold=1 # Smallest distance a gap between can occur.
) -> T:

    return geom
