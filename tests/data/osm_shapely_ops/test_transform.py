import unittest
from shapely.geometry import Point, MultiPoint, \
    LineString, MultiLineString, \
    Polygon, MultiPolygon

from map_engraver.data import osm_shapely_ops
from map_engraver.data.osm_shapely.osm_line_string import OsmLineString
from map_engraver.data.osm_shapely.osm_point import OsmPoint
from map_engraver.data.osm_shapely.osm_polygon import OsmPolygon
from map_engraver.data.osm_shapely_ops.transform import \
    transform_interpolated_euclidean


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

    def test_transform_interpolated_euclidean(self):
        # A pretend projection function that is easy to understand.
        def faux_transformation(x, y):
            return x * x * x, y * y * y

        transformed_point = transform_interpolated_euclidean(
            faux_transformation,
            Point(1, 2)
        )
        assert list(transformed_point.coords) == [(1, 8)]

        transformed_multi_point = transform_interpolated_euclidean(
            faux_transformation,
            MultiPoint([(1, 2), (2, 3), (3, 4)])
        )
        assert transformed_multi_point.bounds == (1, 8, 27, 64)

        transformed_line_string = transform_interpolated_euclidean(
            faux_transformation,
            LineString([(1, 2), (2, 3), (3, 4)])
        )
        assert transformed_line_string.bounds == (1, 8, 27, 64)
        assert len(transformed_line_string.coords) == 12

        transformed_multi_line_string = transform_interpolated_euclidean(
            faux_transformation,
            MultiLineString([
                [(1, 2), (2, 3), (3, 4)],
                [(-1, -2), (-2, -3), (-3, -4)]
            ])
        )
        assert transformed_multi_line_string.bounds == (-27, -64, 27, 64)
        assert len(transformed_multi_line_string.geoms[0].coords) == 12
        assert len(transformed_multi_line_string.geoms[1].coords) == 12

        # Empty objects are a thing in shapely, so we need to test that we can
        # still handle them!
        transformed_empty_line_string = transform_interpolated_euclidean(
            faux_transformation,
            LineString()
        )
        assert transformed_empty_line_string.is_empty

        # Polygon with exterior and interiors.
        transformed_polygon = transform_interpolated_euclidean(
            faux_transformation,
            Polygon(
                [(1, 1), (1, 4), (4, 4), (4, 1), (1, 1)],
                [[(2, 2), (2, 3), (3, 3), (3, 2), (2, 2)]]
            )
        )
        assert transformed_polygon.bounds == (1, 1, 64, 64)
        assert transformed_polygon.exterior.bounds == (1, 1, 64, 64)
        assert len(transformed_polygon.interiors) == 1
        assert transformed_polygon.interiors[0].bounds == (8, 8, 27, 27)

        # Finally, MultiPolygons!
        transformed_multi_polygon = transform_interpolated_euclidean(
            faux_transformation,
            MultiPolygon(
                [
                    (
                        [(1, 1), (1, 4), (4, 4), (4, 1), (1, 1)],
                        [[(2, 2), (2, 3), (3, 3), (3, 2), (2, 2)]]
                    ),
                    (
                        [(-1, -1), (-1, -4), (-4, -4), (-4, -1), (-1, -1)],
                        [[(-2, -2), (-2, -3), (-3, -3), (-3, -2), (-2, -2)]]
                    )
                ]
            )
        )
        assert transformed_multi_polygon.bounds == (-64, -64, 64, 64)
        assert len(transformed_multi_polygon.geoms) == 2
        assert len(transformed_multi_polygon.geoms[0].exterior.coords) == \
               5
        assert len(transformed_multi_polygon.geoms[1].exterior.coords) == \
               5
        assert transformed_multi_polygon.geoms[0].exterior.bounds == \
               (1, 1, 64, 64)
        assert transformed_multi_polygon.geoms[1].exterior.bounds == \
               (-64, -64, -1, -1)
        assert len(transformed_multi_polygon.geoms[0].interiors) == 1
        assert len(transformed_multi_polygon.geoms[1].interiors) == 1
        assert transformed_multi_polygon.geoms[0].interiors[0].bounds == \
               (8, 8, 27, 27)
        assert transformed_multi_polygon.geoms[1].interiors[0].bounds == \
               (-27, -27, -8, -8)

    def test_transform_interpolated_euclidean_handles_inf_safely(self):
        # A fake function that returns invalid coordinates if the coordinate
        # exists between two points.
        def faux_transformation(x, y):
            if 1 < x < 3:
                return float('inf'), float('inf')
            return x, y

        transformed_line_string = transform_interpolated_euclidean(
            faux_transformation,
            LineString([(1, 1), (2, 2), (3, 3)])
        )
        assert list(transformed_line_string.coords) == [
            (1, 1),
            (float('inf'), float('inf')),
            (3, 3)
        ]
        assert len(transformed_line_string.coords) == 3
