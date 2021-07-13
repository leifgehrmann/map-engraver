from pathlib import Path

import unittest

from mapengraver.data.osm import Parser
from mapengraver.transformers.osm_to_shapely import OsmToShapely


class TestOsmToShapely(unittest.TestCase):
    def test_conversion(self):
        path = Path(__file__).parent.joinpath('data.osm')

        osm_map = Parser.parse(path)
        osm_to_shapely = OsmToShapely(osm_map)

        highway_service_way = osm_map.get_way('-101873')
        highway_service_linestring = osm_to_shapely.way_to_linestring(
            highway_service_way
        )

        assert list(highway_service_linestring.coords) == [
            (5.71135378422, 59.00609795619),
            (5.71135378422, 59.01678200227),
            (5.72491834501, 59.01675888021)
        ]
        assert highway_service_linestring.osm_tags['highway'] == 'service'

        bank_building_way = osm_map.get_way('-101787')
        bank_building_polygon = osm_to_shapely.way_to_polygon(bank_building_way)

        assert list(bank_building_polygon.exterior.coords) == [
            (5.71666872951, 59.01328584519), (5.73319773074, 59.01333209396),
            (5.73327340446, 59.00616275303), (5.71674440323, 59.00611649462),
            (5.71666872951, 59.01328584519)
        ]
        assert bank_building_polygon.osm_tags['building'] == 'yes'

        building_relation = osm_map.get_relation('-99750')
        building_polygon = osm_to_shapely.relation_to_polygon(building_relation)
        assert list(building_polygon.exterior.coords) == [
            (5.73921644314, 59.01319334747), (5.75349906139, 59.01296272491),
            (5.75341159278, 59.00625219859), (5.73912661162, 59.0063015675),
            (5.73921644314, 59.01319334747)
        ]
        assert building_polygon.osm_tags['building'] == 'yes'

