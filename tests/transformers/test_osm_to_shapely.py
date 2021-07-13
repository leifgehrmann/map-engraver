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
        assert list(building_polygon.interiors[0].coords) == [
            (5.74469616638, 59.01051080523), (5.74469616638, 59.00847563368),
            (5.7491877428, 59.00847563368), (5.7491877428, 59.01051080523),
            (5.74469616638, 59.01051080523)
        ]
        assert building_polygon.osm_tags['building'] == 'yes'

        water_relation = osm_map.get_relation('-99778')
        water_polygon = osm_to_shapely.relation_to_polygon(water_relation)
        print(list(water_polygon.exterior.coords))
        assert list(water_polygon.exterior.coords) == [
            (5.77204331465, 59.0082363528), (5.7695647063, 59.00678458244),
            (5.76627727032, 59.00629616253), (5.76186221583, 59.00717558346),
            (5.76043653901, 59.00817618663), (5.75981851101, 59.00955560977),
            (5.76088420881, 59.01140894493), (5.76378628992, 59.01263494747),
            (5.76752463333, 59.01281118926), (5.77081092363, 59.0118769482),
            (5.77251263289, 59.01015411586), (5.77204331465, 59.0082363528)
        ]
        assert water_polygon.osm_tags['natural'] == 'water'

