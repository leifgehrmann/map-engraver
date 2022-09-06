import unittest
from shapely.geometry import \
    Polygon, MultiPolygon, \
    LineString, MultiLineString, \
    GeometryCollection

from map_engraver.data.osm_shapely_ops.homogenize import \
    geoms_to_multi_polygon, \
    geoms_to_multi_line_string


class TestHomogenize(unittest.TestCase):
    def test_geoms_to_multi_polygon(self):
        polygon_a = Polygon([(0, 0), (1, 0), (0, 1), (0, 0)])
        polygon_b = Polygon([(2, 2), (2, 1), (1, 2), (2, 2)])
        polygon_c = Polygon([(3, 3), (3, 4), (4, 4), (4, 3), (3, 3)])
        multi_polygon = MultiPolygon([polygon_a, polygon_b])
        line_string = LineString([(0, 0), (1, 0)])
        geometry_collection = GeometryCollection([
            multi_polygon, polygon_c, line_string
        ])

        self.assertEqual(
            MultiPolygon([polygon_a]),
            geoms_to_multi_polygon(polygon_a)
        )

        self.assertEqual(
            multi_polygon,
            geoms_to_multi_polygon(multi_polygon)
        )

        self.assertEqual(
            MultiPolygon([polygon_a, polygon_b, polygon_c]),
            geoms_to_multi_polygon(geometry_collection)
        )

        self.assertEqual(
            MultiPolygon(),
            geoms_to_multi_polygon(Polygon())
        )

    def test_geoms_to_multi_line_string(self):
        line_string_a = LineString([(0, 0), (1, 0), (0, 1)])
        line_string_b = LineString([(2, 2), (2, 1), (1, 2)])
        line_string_c = LineString([(3, 3), (3, 4), (4, 4), (4, 3)])
        multi_line_string = MultiLineString([line_string_a, line_string_b])
        polygon = Polygon([(0, 0), (1, 0), (0, 1)])
        geometry_collection = GeometryCollection([
            multi_line_string, line_string_c, polygon
        ])

        self.assertEqual(
            MultiLineString([line_string_a]),
            geoms_to_multi_line_string(line_string_a)
        )

        self.assertEqual(
            multi_line_string,
            geoms_to_multi_line_string(multi_line_string)
        )

        self.assertEqual(
            MultiLineString([line_string_a, line_string_b, line_string_c]),
            geoms_to_multi_line_string(geometry_collection)
        )

        self.assertEqual(
            MultiLineString(),
            geoms_to_multi_line_string(LineString())
        )
