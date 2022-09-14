from pathlib import Path

from shapely.geometry import MultiPolygon, MultiLineString, LineString

from map_engraver.data.osm import Parser
from map_engraver.data.osm_shapely.osm_to_shapely import OsmToShapely
from map_engraver.data.proj.geodesics import interpolate_geodesic
from tests.data.proj.geodesic_cases import get_geodesic_test_cases


def get_world_map() -> MultiPolygon:
    path = Path(__file__).parent.joinpath('world.osm')

    osm_map = Parser.parse(path)
    osm_to_shapely = OsmToShapely(osm_map)

    polygons = map(osm_to_shapely.way_to_polygon, osm_map.ways.values())
    return MultiPolygon(polygons)


def get_flight_paths() -> MultiLineString:
    line_strings = []
    for case in get_geodesic_test_cases():
        line_string = LineString(case['lineString'])
        line_strings.append(line_string)
    return interpolate_geodesic(MultiLineString(line_strings))
