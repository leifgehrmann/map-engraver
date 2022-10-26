from pathlib import Path

import unittest

from map_engraver.data.osm import Parser
from map_engraver.data.osm_shapely.osm_to_shapely import OsmToShapely, \
    WayToPolygonError


class TestOsmToShapely(unittest.TestCase):
    def test_conversion(self):
        path = Path(__file__).parent.joinpath('data.osm')

        osm_map = Parser.parse(path)
        osm_to_shapely = OsmToShapely(osm_map)

        # Node to Point
        bus_stop_beta_node = osm_map.get_node('-101814')
        bus_stop_beta_point = osm_to_shapely.node_to_point(
            bus_stop_beta_node
        )
        assert list(bus_stop_beta_point.coords) == [
            (59.01678200227, 5.71135378422),
        ]

        # Nodes to Points
        nodes_to_query = {
            '-101814': osm_map.get_node('-101814'),
            '-101818': osm_map.get_node('-101818')
        }
        points = osm_to_shapely.nodes_to_points(
            nodes_to_query
        )
        assert len(points) == 2
        assert list(points['-101814'].coords) == [
            (59.01678200227, 5.71135378422)
        ]
        assert list(points['-101818'].coords) == [
            (59.0163426805, 5.75348477105)
        ]

        # Way to LineString
        highway_service_way = osm_map.get_way('-101873')
        highway_service_line_string = osm_to_shapely.way_to_line_string(
            highway_service_way
        )
        assert list(highway_service_line_string.coords) == [
            (59.00609795619, 5.71135378422),
            (59.01678200227, 5.71135378422),
            (59.01675888021, 5.72491834501)
        ]

        # Ways to LineStrings
        highway_service_ways_to_query = {
            '-101873': osm_map.get_way('-101873'),
            '-101889': osm_map.get_way('-101889')
        }
        highway_service_line_strings = osm_to_shapely.ways_to_line_strings(
            highway_service_ways_to_query
        )
        assert len(highway_service_line_strings) == 2
        assert list(highway_service_line_strings['-101873'].coords) == [
            (59.00609795619, 5.71135378422),
            (59.01678200227, 5.71135378422),
            (59.01675888021, 5.72491834501)
        ]

        # Way to Polygon (With Clock-Wise Ways)
        cw_bank_building_way = osm_map.get_way('-101787')
        cw_bank_building_polygon = osm_to_shapely.way_to_polygon(
            cw_bank_building_way
        )
        assert list(cw_bank_building_polygon.exterior.coords) == [
            (59.01328584519, 5.71666872951), (59.00611649462, 5.71674440323),
            (59.00616275303, 5.73327340446), (59.01333209396, 5.73319773074),
            (59.01328584519, 5.71666872951)
        ]

        # Way to Polygon (With Counter Clock-Wise Ways)
        ccw_bank_building_way = osm_map.get_way('-102178')
        ccw_bank_building_polygon = osm_to_shapely.way_to_polygon(
            ccw_bank_building_way
        )
        assert list(ccw_bank_building_polygon.exterior.coords) == [
            (59.0023220992, 5.71703365152), (58.99515046446, 5.71710932524),
            (58.99519673761, 5.73363832647), (59.00236836271, 5.73356265275),
            (59.0023220992, 5.71703365152)
        ]

        # Ways to Polygons
        building_ways_to_query = {
            '-101787': osm_map.get_way('-101787'),
            '-102178': osm_map.get_way('-102178')
        }
        building_polygons = osm_to_shapely.ways_to_polygons(
            building_ways_to_query
        )
        assert len(building_polygons) == 2
        assert list(building_polygons['-102178'].exterior.coords) == [
            (59.0023220992, 5.71703365152), (58.99515046446, 5.71710932524),
            (58.99519673761, 5.73363832647), (59.00236836271, 5.73356265275),
            (59.0023220992, 5.71703365152)
        ]

        # Relation to MultiPolygon (With Clock-Wise Ways)
        cw_building_relation = osm_map.get_relation('-99750')
        cw_building_multi_polygon = osm_to_shapely.relation_to_multi_polygon(
            cw_building_relation
        )
        assert list(cw_building_multi_polygon.geoms[0].exterior.coords) == [
            (59.01319334747, 5.73921644314), (59.0063015675, 5.73912661162),
            (59.00625219859, 5.75341159278), (59.01296272491, 5.75349906139),
            (59.01319334747, 5.73921644314)
        ]
        assert list(cw_building_multi_polygon.geoms[0].interiors[0].coords) \
               == [
            (59.01051080523, 5.74469616638), (59.01051080523, 5.7491877428),
            (59.00847563368, 5.7491877428), (59.00847563368, 5.74469616638),
            (59.01051080523, 5.74469616638)
        ]

        # Relation to MultiPolygon (With Counter Clock-Wise Ways)
        ccw_building_relation = osm_map.get_relation('-99893')
        ccw_building_multi_polygon = osm_to_shapely.relation_to_multi_polygon(
            ccw_building_relation
        )
        assert list(ccw_building_multi_polygon.geoms[0].exterior.coords) == [
            (59.00198690218, 5.73956674445), (58.99518412812, 5.73939352771),
            (58.99508762548, 5.75367843649), (59.00189041861, 5.75385165323),
            (59.00198690218, 5.73956674445)
        ]
        assert list(ccw_building_multi_polygon.geoms[0].interiors[0].coords) \
               == [
            (58.99937088385, 5.74500532962), (58.99937088385, 5.74949690604),
            (58.99733505352, 5.74949690604), (58.99733505352, 5.74500532962),
            (58.99937088385, 5.74500532962)
        ]

        # Relation to MultiPolygon (With multiple Way segments)
        water_relation = osm_map.get_relation('-99778')
        water_polygon = osm_to_shapely.relation_to_multi_polygon(
            water_relation
        )
        assert list(water_polygon.geoms[0].exterior.coords) == [
            (59.0082363528, 5.77204331465),
            (59.01015411586, 5.77251263289),
            (59.0118769482, 5.77081092363),
            (59.01281118926, 5.76752463333),
            (59.01263494747, 5.76378628992),
            (59.01140894493, 5.76088420881),
            (59.00955560977, 5.75981851101),
            (59.00817618663, 5.76043653901),
            (59.00717558346, 5.76186221583),
            (59.00629616253, 5.76627727032),
            (59.00678458244, 5.7695647063),
            (59.0082363528, 5.77204331465),
        ]

        # Relation to MultiPolygon (With multiple outer ways)
        relation_with_multiple_exteriors = osm_map.get_relation('-99805')
        multi_polygon = osm_to_shapely.relation_to_multi_polygon(
            relation_with_multiple_exteriors
        )
        assert len(multi_polygon.geoms) == 2
        assert len(multi_polygon.geoms[0].interiors) == 0
        assert len(multi_polygon.geoms[1].interiors) == 1
        assert list(multi_polygon.geoms[0].exterior.coords) == [
            (59.01294872348, 5.79411162062),
            (59.0061481157, 5.79393840388),
            (59.0060516438, 5.80822331266),
            (59.01285227064, 5.8083965294),
            (59.01294872348, 5.79411162062)
        ]
        assert list(multi_polygon.geoms[1].exterior.coords) == [
            (59.01303598673, 5.77686022151),
            (59.0062353962, 5.77668700477),
            (59.00613892454, 5.79097191354),
            (59.01293953413, 5.79114513029),
            (59.01303598673, 5.77686022151)
        ]
        assert list(multi_polygon.geoms[1].interiors[0].coords) == [
            (59.01042080809, 5.78229880667),
            (59.01042080809, 5.78679038309),
            (59.00838563122, 5.78679038309),
            (59.00838563122, 5.78229880667),
            (59.01042080809, 5.78229880667)
        ]

        # Relations to MultiPolygons
        relations_to_query = {
            '-99778': osm_map.get_relation('-99778'),
            '-99805': osm_map.get_relation('-99805')
        }
        multi_polygons = osm_to_shapely.relations_to_multi_polygons(
            relations_to_query
        )
        assert len(multi_polygons) == 2

    def test_conversion_fails_for_invalid_types(self):
        path = Path(__file__).parent.joinpath('data.osm')

        osm_map = Parser.parse(path)
        osm_to_shapely = OsmToShapely(osm_map)

        highway_service_way = osm_map.get_way('-101873')
        with self.assertRaises(WayToPolygonError):
            osm_to_shapely.way_to_polygon(highway_service_way)

    def test_incomplete_refs_handler(self):
        path = Path(__file__).parent.joinpath('incomplete_data.osm')

        osm_map = Parser.parse(path)
        osm_to_shapely = OsmToShapely(osm_map)
        incomplete_relation = osm_map.get_relation('-99898')
        incomplete_elements = []
        incomplete_refs = []

        incomplete_polygon = osm_to_shapely.relation_to_multi_polygon(
            incomplete_relation
        )
        assert incomplete_polygon is None

        osm_to_shapely.incomplete_refs_handler = lambda element, refs: \
            incomplete_elements.append(element) and \
            incomplete_refs.append(refs)

        incomplete_polygon = osm_to_shapely.relation_to_multi_polygon(
            incomplete_relation
        )
        assert incomplete_polygon is None
        assert incomplete_elements[0] == incomplete_relation
        assert len(incomplete_refs) == 0
