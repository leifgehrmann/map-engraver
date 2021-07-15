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

    def test_conversion(self):
        wgs_84_identity_func = build_projection_function()
        self.assert_coordinates_are_close(
            wgs_84_identity_func(55.855529, -4.232459),
            (55.855529, -5.232459)
        )

        british_grid_func = build_projection_function(
            output_crs=pyproj.CRS.from_epsg(27700)
        )
        self.assert_coordinates_are_close(
            british_grid_func(55.855529, -4.232459),
            (260354.7929476458, 664735.6993417306)
        )
