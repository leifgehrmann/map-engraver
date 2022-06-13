import unittest
from shapely.geometry import Polygon, MultiPolygon, LineString, \
    GeometryCollection

from map_engraver.data.osm_shapely_ops.homogenize import geoms_to_multi_polygon


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
        pass
