import unittest
from typing import Tuple
from math import isclose
from pathlib import Path

from pyproj import CRS, Transformer
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry.base import BaseGeometry

from map_engraver.data.proj.azimuthal_masks import azimuthal_mask, \
    azimuthal_mask_wgs84
from tests.data.proj.azimuthal_cases import get_azimuthal_test_cases


class TestAzimuthalMasks(unittest.TestCase):
    def test_azimuthal_mask_raises_error_for_unsupported_proj(self):
        unsupported_projs = [
            '+proj=aeqd',
            '+proj=airy',
            '+proj=hammer',
            '+proj=laea',
            '+proj=lee_os',
            '+proj=mil_os',
            '+proj=gs48',
            '+proj=gs50',
            '+proj=alsk',
            '+proj=oea +m=1 +n=2',
            '+proj=stere +lat_0=90 +lat_ts=75',
            '+proj=sterea +lat_0=90',
        ]
        for unsupported_proj in unsupported_projs:
            crs = CRS.from_proj4(unsupported_proj)
            with self.assertRaises(Exception):
                azimuthal_mask(crs)
            with self.assertRaises(Exception):
                azimuthal_mask_wgs84(crs)

    def test_azimuthal_mask_outputs_expected_polygons(self):
        for case in get_azimuthal_test_cases():
            crs = CRS.from_proj4(case['proj4'])
            mask = azimuthal_mask(crs)
            assert mask.is_valid
            assert mask.is_simple
            self.assert_mask_has_bounds(mask, case['expectedProjBounds'])

    def test_azimuthal_mask_throws_error_on_unsupported_proj(self):
        crs = CRS.from_epsg(4326)
        with self.assertRaises(Exception):
            azimuthal_mask(crs)

    def test_azimuthal_mask_wgs84_outputs_expected_multi_polygons(self):
        for case in get_azimuthal_test_cases():
            crs = CRS.from_proj4(case['proj4'])
            mask = azimuthal_mask_wgs84(crs)
            self.assert_geoms_are_valid(mask)
            self.assert_all_points_are_valid(crs, mask)
            self.assert_all_mid_points_are_valid(crs, mask)
            self.assert_mask_has_bounds(mask, case['expectedWgs84Bounds'])
            self.assert_mask_geom_count(mask, case['expectedWgs84GeomsCount'])

    def test_azimuthal_mask_wgs84_throws_error_on_unsupported_proj(self):
        crs = CRS.from_epsg(4326)
        with self.assertRaises(Exception):
            azimuthal_mask_wgs84(crs)

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
                assert transformer.transform(*point)[0] != float('inf')

    @staticmethod
    def assert_all_mid_points_are_valid(
            crs: CRS,
            mask: MultiPolygon
    ):
        transformer = Transformer.from_proj(
            CRS.from_epsg(4326),
            crs
        )
        geom: Polygon
        for geom in mask.geoms:
            for i in range(len(geom.exterior.coords) - 1):
                a = geom.exterior.coords[i]
                b = geom.exterior.coords[i + 1]
                m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                assert transformer.transform(*m)[0] != float('inf')

                # Todo: This commented-out test proves this algorithm is not
                #  completely reliable. For context, see the function
                #  documentation of `azimuthal_mask_wgs84`.
                # Take a subsample of 100 points, just to check that all points
                # between `a` and `b` are valid coordinates in the `crs`.
                # failed = False
                # for r in range(100):
                #    r_a = r / 100
                #    r_b = 1 - r_a
                #    m = ((a[0] * r_a + b[0] * r_b),
                #         (a[1] * r_a + b[1] * r_b))
                #    if transformer.transform(*m)[0] == float('inf'):
                #        failed = True
                #        print(r)
                #        print(a)
                #        print(b)
                #        print(m)
                #    # assert transformer.transform(*m)[0] != float('inf')
                # if failed:
                #    print('-------')
                #    assert not failed

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
