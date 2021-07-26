import pyproj
import unittest

from map_engraver.transformers.geo_coordinate import GeoCoordinate
from map_engraver.transformers.geo_coordinate_transformers import \
    transform_geo_coordinates_to_new_crs


class TestGeoCoordinateTransformers(unittest.TestCase):
    def test_tuple_transformers(self):
        wgs84_crs = pyproj.CRS.from_epsg(4326)
        british_crs = pyproj.CRS.from_epsg(27700)
        input_coordinates = [
            GeoCoordinate(325600, 673400, british_crs),
            GeoCoordinate(325900, 673700, british_crs)
        ]
        output_coordinates = transform_geo_coordinates_to_new_crs(
            input_coordinates,
            wgs84_crs
        )

        assert type(output_coordinates) is list

        coord_0 = output_coordinates[0]
        self.assertAlmostEqual(coord_0.x, 55.947853536820716)
        self.assertAlmostEqual(coord_0.y, -3.1928925390669995)

        coord_1 = output_coordinates[1]
        self.assertAlmostEqual(coord_1.x, 55.950594791166964)
        self.assertAlmostEqual(coord_1.y, -3.188172556436762)
