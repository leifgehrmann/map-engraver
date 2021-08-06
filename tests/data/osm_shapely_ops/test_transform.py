import unittest
from shapely.geometry import Point

from map_engraver.data import osm_shapely_ops
from map_engraver.data.osm_shapely.osm_line_string import OsmLineString
from map_engraver.data.osm_shapely.osm_point import OsmPoint
from map_engraver.data.osm_shapely.osm_polygon import OsmPolygon


class TestTransform(unittest.TestCase):
    def test_line_string_is_transformed(self):
        geom = OsmLineString([
            (1, 2),
            (3, 4),
            (5, 6),
            (7, 8),
        ])
        geom.osm_tags = {
            'hello': 'world'
        }
        new_geom = osm_shapely_ops.transform(
            lambda x, y: (x * 2.0, y * 3.0),
            geom
        )

        assert list(new_geom.coords) == [
            (2, 6),
            (6, 12),
            (10, 18),
            (14, 24)
        ]
        assert new_geom.osm_tags['hello'] == 'world'

    def test_point_is_transformed(self):
        geom = OsmPoint(2, 3)
        geom.osm_tags = {
            'hello': 'world'
        }
        new_geom = osm_shapely_ops.transform(
            lambda x, y: (x * 2.0, y * 3.0),
            geom
        )

        assert new_geom.x == 4
        assert new_geom.y == 9
        assert new_geom.osm_tags['hello'] == 'world'

    def test_polygon_is_transformed(self):
        geom = OsmPolygon([
            (1, 2),
            (3, 4),
            (5, 6),
            (1, 2),
        ])
        geom.osm_tags = {
            'hello': 'world'
        }
        new_geom = osm_shapely_ops.transform(
            lambda x, y: (x * 2.0, y * 3.0),
            geom
        )

        assert list(new_geom.exterior.coords) == [
            (2, 6),
            (6, 12),
            (10, 18),
            (2, 6)
        ]
        assert new_geom.osm_tags['hello'] == 'world'

    def test_non_osm_class_raises_error(self):
        with self.assertRaises(RuntimeError):
            osm_shapely_ops.transform(
                lambda x, y: (x * 2.0, y * 3.0),
                Point(1, 2)
            )
