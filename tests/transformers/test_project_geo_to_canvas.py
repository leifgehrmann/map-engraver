import math

from typing import Tuple

import pyproj
import unittest

from mapengraver.transformers.project_geo_to_canvas import \
    build_projection_function


class TestProjectGeoToCanvas(unittest.TestCase):
    @staticmethod
    def assert_coordinates_are_close(
            expected_coordinate: Tuple[float, float],
            actual_coordinate: Tuple[float, float]
    ):
        if not math.isclose(expected_coordinate[0], actual_coordinate[0]) or \
                not math.isclose(expected_coordinate[1], actual_coordinate[1]):
            raise AssertionError(
                'Coordinates are not close. Expected: (' +
                str(expected_coordinate[0]) + ', ' +
                str(expected_coordinate[1]) +
                '). Actual: (' +
                str(actual_coordinate[0]) + ', ' +
                str(actual_coordinate[1]) + ')'
            )

    @staticmethod
    def magnitude(v: Tuple[float, float]):
        return math.sqrt(v[0] * v[0] + v[1] * v[1])

    def test_identity_conversion(self):
        wgs_84_identity_func = build_projection_function()
        self.assert_coordinates_are_close(
            wgs_84_identity_func(55.855529, -4.232459),
            (55.855529, -4.232459)
        )

    def test_british_national_grid_conversion(self):
        british_grid_func = build_projection_function(
            # 27700 is the british national grid
            output_crs=pyproj.CRS.from_epsg(27700)
        )
        self.assert_coordinates_are_close(
            # Glasgow
            british_grid_func(55.855529, -4.232459),
            (260354.7929476458, 664735.6993417306)
        )

    def test_offset_conversion(self):
        wgs84_crs = pyproj.CRS.from_epsg(4326)
        british_crs = pyproj.CRS.from_epsg(27700)
        crs_transformer = pyproj.Transformer.from_proj(
            wgs84_crs,
            british_crs
        )
        walter_scott_monument_wgs84 = (55.86115, -4.25017)
        glasgow_central_station_wgs84 = (55.86045, -4.25772)
        walter_scott_column_british = crs_transformer.transform(
            *walter_scott_monument_wgs84
        )
        glasgow_func = build_projection_function(
            input_crs=wgs84_crs,
            output_crs=british_crs,
            output_origin=walter_scott_column_british
        )
        actual_distance_between_poi = math.floor(self.magnitude(
            glasgow_func(*glasgow_central_station_wgs84)
        ))
        expected_distance_between_poi = 479
        assert math.isclose(
            actual_distance_between_poi,
            expected_distance_between_poi
        )
