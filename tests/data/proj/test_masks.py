import unittest
from typing import Tuple
from math import isclose
from pathlib import Path

from pyproj import CRS, Transformer
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry.base import BaseGeometry

from map_engraver.data.proj.masks import orthographic_mask, \
    orthographic_mask_wgs84
from tests.data.proj.orthographic_cases import get_orthographic_test_cases


class TestMasks(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_orthographic_mask_outputs_expected_polygons(self):
        for case in get_orthographic_test_cases():
            crs = CRS.from_proj4(case['proj4'])
            mask = orthographic_mask(crs)
            assert mask.is_valid
            assert mask.is_simple
            self.assert_mask_has_bounds(mask, case['expectedProjBounds'])

    def test_orthographic_mask_throws_error_on_unsupported_proj(self):
        crs = CRS.from_epsg(4326)
        with self.assertRaises(Exception):
            orthographic_mask(crs)

    def test_orthographic_mask_wgs84_outputs_expected_multi_polygons(self):
        for case in get_orthographic_test_cases():
            crs = CRS.from_proj4(case['proj4'])
            mask = orthographic_mask_wgs84(crs)
            self.assert_geoms_are_valid(mask)
            self.assert_all_points_are_valid(crs, mask)
            self.assert_mask_has_bounds(mask, case['expectedWgs84Bounds'])
            self.assert_mask_geom_count(mask, case['expectedWgs84GeomsCount'])

    def test_orthographic_mask_wgs84_throws_error_on_unsupported_proj(self):
        crs = CRS.from_epsg(4326)
        with self.assertRaises(Exception):
            orthographic_mask_wgs84(crs)

    @staticmethod
    def assert_geoms_are_valid(
            mask: MultiPolygon
    ):
        geom: Polygon
        for geom in mask.geoms:
            assert geom.is_valid
            assert geom.is_simple

    @staticmethod
    def assert_all_points_are_valid(
            crs: CRS,
            mask: MultiPolygon
    ):
        transformer = Transformer.from_proj(
            CRS.from_epsg(4326),
            crs
        )
        geom: Polygon
        for geom in mask.geoms:
            for point in geom.exterior.coords:
                assert transformer.transform(*point) != float('inf')

    @staticmethod
    def assert_mask_has_bounds(
            mask: BaseGeometry,
            expected_bounds: Tuple[float, float, float, float],
    ):
        if (
            not isclose(mask.bounds[0], expected_bounds[0], abs_tol=0.1) or
            not isclose(mask.bounds[1], expected_bounds[1], abs_tol=0.1) or
            not isclose(mask.bounds[2], expected_bounds[2], abs_tol=0.1) or
            not isclose(mask.bounds[3], expected_bounds[3], abs_tol=0.1)
        ):
            raise AssertionError(
                'Bounds are not close. Expected: (' +
                str(expected_bounds) +
                '). Actual: (' +
                str(mask.bounds) +
                ')'
            )

    @staticmethod
    def assert_mask_geom_count(
            mask: MultiPolygon,
            expected_geom_count: int
    ):
        if len(mask.geoms) != expected_geom_count:
            raise AssertionError(
                'Geom counts are not close. Expected: (' +
                str(expected_geom_count) +
                '). Actual: (' +
                str(len(mask.geoms)) +
                ')'
            )
