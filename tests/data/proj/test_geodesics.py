from math import isclose

from typing import Tuple, List

import unittest
from shapely.geometry import LineString, MultiLineString, Polygon

from map_engraver.data.proj.geodesics import interpolate_geodesic
from tests.data.proj.geodesic_cases import get_geodesic_test_cases


class TestGeodesics(unittest.TestCase):
    def test_interpolate_geodesic_for_line_string(self):
        for case in get_geodesic_test_cases():
            input_line_string = LineString(case['lineString'])
            output_line_string = interpolate_geodesic(input_line_string)

            TestGeodesics.assert_output_matches_expected(
                output_line_string,
                case['expectedGeomsBounds']
            )

    def test_interpolate_geodesic_does_not_support_polygons(self):
        with self.assertRaises(Exception):
            # noinspection PyTypeChecker
            interpolate_geodesic(Polygon([(0, 0), (1, 1), (1, 0), (0, 0)]))

    @staticmethod
    def assert_output_matches_expected(
            output: MultiLineString,
            expected_geoms_bounds: List[Tuple[float, float, float, float]]
    ):
        actual_geoms: List[LineString] = output.geoms
        assert len(actual_geoms) == len(expected_geoms_bounds)
        for i in range(len(expected_geoms_bounds)):
            actual_geom_bounds = actual_geoms[i].bounds
            expected_geom_bounds = expected_geoms_bounds[i]
            TestGeodesics.assert_bounds_are_similar(
                expected_geom_bounds,
                actual_geom_bounds
            )

    @staticmethod
    def assert_bounds_are_similar(
            expected_bounds: Tuple[float, float, float, float],
            actual_bounds: Tuple[float, float, float, float]
    ):
        if (
            not isclose(actual_bounds[0], expected_bounds[0], abs_tol=0.1) or
            not isclose(actual_bounds[1], expected_bounds[1], abs_tol=0.1) or
            not isclose(actual_bounds[2], expected_bounds[2], abs_tol=0.1) or
            not isclose(actual_bounds[3], expected_bounds[3], abs_tol=0.1)
        ):
            raise AssertionError(
                'Bounds are not close. Expected: (' +
                str(expected_bounds) +
                '). Actual: (' +
                str(actual_bounds) +
                ')'
            )
