from math import isclose

import re

from typing import Tuple

import pyproj
from pathlib import Path

import unittest
from pyproj import CRS, Transformer
from shapely import ops
from shapely.geometry import Polygon, MultiPolygon

from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu

from map_engraver.canvas import CanvasBuilder
from map_engraver.data import geo_canvas_ops
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.proj.masks import orthographic_mask
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer


class TestMasks(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_orthographic_masks_at_equator(self):
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
            mask = orthographic_mask(crs)
            self.draw_mask_wgs84(case['proj4'], mask)
            self.assert_geoms_are_valid(mask)
            self.assert_all_points_are_valid(crs, mask)
            self.assert_mask_has_bounds(mask, case['expectedBounds'])
            self.assert_mask_geom_count(mask, case['expectedGeomsCount'])

    def test_orthographic_masks_at_45_north(self):
        pass

    def test_orthographic_masks_at_north_pole(self):
        pass

    def test_orthographic_masks_at_anti_meridian(self):
        pass

    @staticmethod
    def draw_mask_wgs84(name: str, mask_wgs84: MultiPolygon):
        name = re.sub(r'[^0-9A-Za-z_-]', '', name)
        path = Path(__file__).parent.joinpath(
            'output/%s.svg' % name
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(
            Cu.from_px(360 + 20 * 2),
            Cu.from_px(220 + 20 * 2)
        )

        canvas = canvas_builder.build()

        wgs84_crs = pyproj.CRS.from_epsg(4326)

        origin_for_geo = GeoCoordinate(
            0,
            0,
            wgs84_crs
        )
        origin_for_canvas = CanvasCoordinate(
            Cu.from_px(180 + 20),
            Cu.from_px(90 + 20)
        )

        # 1 pixel for every degree
        geo_to_canvas_scale = geo_canvas_ops.GeoCanvasScale(
            1,
            Cu.from_px(1)
        )

        mask_wgs84 = ops.transform(lambda x, y: (y, x), mask_wgs84)

        transformation_func = geo_canvas_ops.build_transformer(
            crs=wgs84_crs,
            data_crs=wgs84_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas
        )

        mask_wgs84 = ops.transform(transformation_func, mask_wgs84)

        domain = Polygon([(-180, -90), (180, -90), (180, 90), (-180, 90)])
        domain = ops.transform(transformation_func, domain)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0, 0, 1)
        polygon_drawer.geoms = [domain]
        polygon_drawer.draw(canvas)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (1, 1, 0)
        polygon_drawer.geoms = [mask_wgs84]
        polygon_drawer.draw(canvas)

        canvas.close()

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
            mask: MultiPolygon,
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
