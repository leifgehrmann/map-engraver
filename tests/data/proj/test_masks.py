import unittest
from typing import Tuple
from math import isclose
from pathlib import Path

from pyproj import CRS, Transformer
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry.base import BaseGeometry

from map_engraver.data.proj.masks import orthographic_mask, \
    orthographic_mask_wgs84


class TestMasks(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_orthographic_mask_outputs_expected_polygons(self):
        cases = [
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=0',
                'expectedBounds': (-89.9, -89.9, 89.9, 89.9)
            },
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=0.1',
                'expectedBounds': (-89.8, -180, 89.9, 180)
            },
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=20',
                'expectedBounds': (-69.9, -180.0, 90.0, 180.0)
            },
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=90',
                'expectedBounds': (0.02, -180.0, 90.0, 180.0)
            },
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=-90',
                'expectedBounds': (-90.0, -180.0, -0.0, 180.0)
            },
            {
                'proj4': '+proj=ortho +lon_0=180 +lat_0=0',
                'expectedBounds': (-89.9, -180, 89.9, 180)
            },
            {
                'proj4': '+proj=ortho +lon_0=180 +lat_0=0.1',
                'expectedBounds': (-89.8, -180, 89.9, 180)
            },
            {
                'proj4': '+proj=ortho +lon_0=180 +lat_0=20',
                'expectedBounds': (-69.9, -180.0, 90.0, 180.0)
            },
            {
                'proj4': '+proj=geos +h=35785831.0 +lon_0=-60 +sweep=x',
                'expectedBounds': (-81.3, -141.2, 81.3, 21.2)
            },
            {
                'proj4': '+proj=geos +h=35785831.0 +lon_0=-160 +sweep=x',
                'expectedBounds': (-81.3, -180.0, 81.3, 180.0)
            },
            {
                'proj4': '+proj=geos +h=35785831.0 +lon_0=-160 +sweep=y',
                'expectedBounds': (-81.3, -180.0, 81.3, 180.0)
            },
            {
                'proj4': '+proj=nsper +h=3000000 +lat_0=-20 +lon_0=-60',
                'expectedBounds': (-67.1, -111.2, 27.1, -8.7)
            },
            {
                'proj4': '+proj=nsper +h=3000000 +lat_0=-20 +lon_0=145',
                'expectedBounds': (-67.1, -180.0, 27.1, 180.0)
            },
            {
                'proj4': '+proj=nsper +h=3000000 +lat_0=-80 +lon_0=145',
                'expectedBounds': (-90.0, -180.0, -32.8, 180.0)
            },
            {
                'proj4': '+proj=tpers +h=5500000 +lat_0=40',
                'expectedBounds': (-17.4, -180.0, 90.0, 180.0)
            },
            {
                'proj4': '+proj=tpers +h=5500000 +lat_0=-40',
                'expectedBounds': (-90.0, -180.0, 17.4, 180.0)
            },
            {
                'proj4': '+proj=tpers +h=5500000 +lat_0=30 +lon_0=-120 '
                         '+tilt=30',
                'expectedBounds': (-27.3, -180.0, 87.5, 180.0),
            },
        ]
        for case in cases:
            crs = CRS.from_proj4(case['proj4'])
            mask = orthographic_mask(crs)
            assert mask.is_valid
            assert mask.is_simple
            # self.assert_mask_has_bounds(mask, case['expectedBounds'])

    def test_orthographic_mask_wgs84_outputs_expected_multi_polygons(self):
        cases = [
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=0',
                'expectedBounds': (-89.9, -89.9, 89.9, 89.9),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=0.1',
                'expectedBounds': (-89.8, -180, 89.9, 180),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=20',
                'expectedBounds': (-69.9, -180.0, 90.0, 180.0),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=90',
                'expectedBounds': (0.02, -180.0, 90.0, 180.0),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=-90',
                'expectedBounds': (-90.0, -180.0, -0.0, 180.0),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=ortho +lon_0=180 +lat_0=0',
                'expectedBounds': (-89.9, -180, 89.9, 180),
                'expectedGeomsCount': 2
            },
            {
                'proj4': '+proj=ortho +lon_0=180 +lat_0=0.1',
                'expectedBounds': (-89.8, -180, 89.9, 180),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=ortho +lon_0=180 +lat_0=20',
                'expectedBounds': (-69.9, -180.0, 90.0, 180.0),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=geos +h=35785831.0 +lon_0=-60 +sweep=x',
                'expectedBounds': (-81.3, -141.2, 81.3, 21.2),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=geos +h=35785831.0 +lon_0=-160 +sweep=x',
                'expectedBounds': (-81.3, -180.0, 81.3, 180.0),
                'expectedGeomsCount': 2
            },
            {
                'proj4': '+proj=geos +h=35785831.0 +lon_0=-160 +sweep=y',
                'expectedBounds': (-81.3, -180.0, 81.3, 180.0),
                'expectedGeomsCount': 2
            },
            {
                'proj4': '+proj=nsper +h=3000000 +lat_0=-20 +lon_0=-60',
                'expectedBounds': (-67.1, -111.2, 27.1, -8.7),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=nsper +h=3000000 +lat_0=-20 +lon_0=145',
                'expectedBounds': (-67.1, -180.0, 27.1, 180.0),
                'expectedGeomsCount': 2
            },
            {
                'proj4': '+proj=nsper +h=3000000 +lat_0=-80 +lon_0=145',
                'expectedBounds': (-90.0, -180.0, -32.8, 180.0),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=tpers +h=5500000 +lat_0=40',
                'expectedBounds': (-17.4, -180.0, 90.0, 180.0),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=tpers +h=5500000 +lat_0=-40',
                'expectedBounds': (-90.0, -180.0, 17.4, 180.0),
                'expectedGeomsCount': 1
            },
            {
                'proj4': '+proj=tpers +h=5500000 +lat_0=30 +lon_0=-120 '
                         '+tilt=30',
                'expectedBounds': (-27.3, -180.0, 87.5, 180.0),
                'expectedGeomsCount': 2
            },
        ]
        for case in cases:
            crs = CRS.from_proj4(case['proj4'])
            mask = orthographic_mask_wgs84(crs)
            self.assert_geoms_are_valid(mask)
            self.assert_all_points_are_valid(crs, mask)
            self.assert_mask_has_bounds(mask, case['expectedBounds'])
            self.assert_mask_geom_count(mask, case['expectedGeomsCount'])

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
