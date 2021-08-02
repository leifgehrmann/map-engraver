from pathlib import Path

import unittest

from map_engraver.data.osm import Parser
from map_engraver.transformers.osm_to_shapely import OsmToShapely, \
    WayToPolygonError, RelationToPolygonError


class TestOsmToShapely(unittest.TestCase):
    def test_conversion(self):
        path = Path(__file__).parent.joinpath('data.osm')

        osm_map = Parser.parse(path)
        osm_to_shapely = OsmToShapely(osm_map)

        bus_stop_beta_node = osm_map.get_node('-101814')
        bus_stop_beta_point = osm_to_shapely.node_to_point(
            bus_stop_beta_node
        )
        assert bus_stop_beta_point.osm_tags['highway'] == 'bus_stop'
        assert list(bus_stop_beta_point.coords) == [
            (5.71135378422, 59.01678200227),
        ]

        highway_service_way = osm_map.get_way('-101873')
        highway_service_linestring = osm_to_shapely.way_to_linestring(
            highway_service_way
        )
        assert highway_service_linestring.osm_tags['highway'] == 'service'
        assert list(highway_service_linestring.coords) == [
            (5.71135378422, 59.00609795619),
            (5.71135378422, 59.01678200227),
            (5.72491834501, 59.01675888021)
        ]

        cw_bank_building_way = osm_map.get_way('-101787')
        cw_bank_building_polygon = osm_to_shapely.way_to_polygon(
            cw_bank_building_way
        )
        assert cw_bank_building_polygon.osm_tags['building'] == 'yes'
        assert list(cw_bank_building_polygon.exterior.coords) == [
            (5.71666872951, 59.01328584519), (5.73319773074, 59.01333209396),
            (5.73327340446, 59.00616275303), (5.71674440323, 59.00611649462),
            (5.71666872951, 59.01328584519)
        ]

        ccw_bank_building_way = osm_map.get_way('-102178')
        ccw_bank_building_polygon = osm_to_shapely.way_to_polygon(
            ccw_bank_building_way
        )
        assert ccw_bank_building_polygon.osm_tags['building'] == 'yes'
        assert list(ccw_bank_building_polygon.exterior.coords) == [
            (5.71703365152, 59.0023220992), (5.73356265275, 59.00236836271),
            (5.73363832647, 58.99519673761), (5.71710932524, 58.99515046446),
            (5.71703365152, 59.0023220992)
        ]

        cw_building_relation = osm_map.get_relation('-99750')
        cw_building_polygon = osm_to_shapely.relation_to_polygon(
            cw_building_relation
        )
        assert cw_building_polygon.osm_tags['building'] == 'yes'
        assert list(cw_building_polygon.exterior.coords) == [
            (5.73921644314, 59.01319334747), (5.75349906139, 59.01296272491),
            (5.75341159278, 59.00625219859), (5.73912661162, 59.0063015675),
            (5.73921644314, 59.01319334747)
        ]
        assert list(cw_building_polygon.interiors[0].coords) == [
            (5.74469616638, 59.01051080523), (5.74469616638, 59.00847563368),
            (5.7491877428, 59.00847563368), (5.7491877428, 59.01051080523),
            (5.74469616638, 59.01051080523)
        ]

        ccw_building_relation = osm_map.get_relation('-99893')
        ccw_building_polygon = osm_to_shapely.relation_to_polygon(
            ccw_building_relation
        )
        assert ccw_building_polygon.osm_tags['building'] == 'yes'
        assert list(ccw_building_polygon.exterior.coords) == [
            (5.73956674445, 59.00198690218), (5.75385165323, 59.00189041861),
            (5.75367843649, 58.99508762548), (5.73939352771, 58.99518412812),
            (5.73956674445, 59.00198690218)
        ]
        assert list(ccw_building_polygon.interiors[0].coords) == [
            (5.74500532962, 58.99937088385), (5.74500532962, 58.99733505352),
            (5.74949690604, 58.99733505352), (5.74949690604, 58.99937088385),
            (5.74500532962, 58.99937088385)
        ]

        water_relation = osm_map.get_relation('-99778')
        water_polygon = osm_to_shapely.relation_to_polygon(water_relation)
        assert water_polygon.osm_tags['natural'] == 'water'
        assert list(water_polygon.exterior.coords) == [
            (5.77204331465, 59.0082363528), (5.7695647063, 59.00678458244),
            (5.76627727032, 59.00629616253), (5.76186221583, 59.00717558346),
            (5.76043653901, 59.00817618663), (5.75981851101, 59.00955560977),
            (5.76088420881, 59.01140894493), (5.76378628992, 59.01263494747),
            (5.76752463333, 59.01281118926), (5.77081092363, 59.0118769482),
            (5.77251263289, 59.01015411586), (5.77204331465, 59.0082363528)
        ]

    def test_conversion_fails_for_invalid_types(self):
        path = Path(__file__).parent.joinpath('data.osm')

        osm_map = Parser.parse(path)
        osm_to_shapely = OsmToShapely(osm_map)

        highway_service_way = osm_map.get_way('-101873')
        with self.assertRaises(WayToPolygonError):
            osm_to_shapely.way_to_polygon(highway_service_way)

    def test_transform(self):
        path = Path(__file__).parent.joinpath('data.osm')

        osm_map = Parser.parse(path)
        osm_to_shapely = OsmToShapely(osm_map, lambda x, y: (0, 0))

        highway_service_way = osm_map.get_way('-101873')
        highway_service_linestring = osm_to_shapely.way_to_linestring(
            highway_service_way
        )
        assert list(highway_service_linestring.coords) == [
            (0, 0), (0, 0), (0, 0)
        ]

    def test_incomplete_refs_handler(self):
        path = Path(__file__).parent.joinpath('incomplete_data.osm')

        osm_map = Parser.parse(path)
        osm_to_shapely = OsmToShapely(osm_map)
        incomplete_relation = osm_map.get_relation('-99898')
        incomplete_elements = []
        incomplete_refs = []

        incomplete_polygon = osm_to_shapely.relation_to_polygon(
            incomplete_relation
        )
        assert incomplete_polygon is None

        osm_to_shapely.incomplete_refs_handler = lambda element, refs: \
            incomplete_elements.append(element) and \
            incomplete_refs.append(refs)

        incomplete_polygon = osm_to_shapely.relation_to_polygon(
            incomplete_relation
        )
        assert incomplete_polygon is None
        assert incomplete_elements[0] == incomplete_relation
        assert len(incomplete_refs) == 0

    def test_multiple_exteriors(self):
        path = Path(__file__).parent.joinpath('unimplemented_data.osm')

        osm_map = Parser.parse(path)
        osm_to_shapely = OsmToShapely(osm_map)

        relation_with_multiple_exteriors = osm_map.get_relation('-99894')
        with self.assertRaises(RelationToPolygonError):
            osm_to_shapely.relation_to_polygon(
                relation_with_multiple_exteriors
            )
