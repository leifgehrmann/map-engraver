import math

from typing import Tuple

import pyproj
import unittest

from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.geo_canvas_ops.geo_canvas_scale import GeoCanvasScale
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers import \
    build_crs_to_canvas_transformer, \
    build_canvas_to_crs_transformer


class TestGeoCanvasTransformers(unittest.TestCase):
    @staticmethod
    def assert_coordinates_are_close(
            expected_coordinate: Tuple[float, float],
            actual_coordinate: Tuple[float, float]
    ):
        if not math.isclose(
                expected_coordinate[0],
                actual_coordinate[0],
                abs_tol=0.01
        ) or not math.isclose(
            expected_coordinate[1],
            actual_coordinate[1],
            abs_tol=0.01
        ):
            raise AssertionError(
                'Coordinates are not close. Expected: (' +
                str(expected_coordinate[0]) + ', ' +
                str(expected_coordinate[1]) +
                '). Actual: (' +
                str(actual_coordinate[0]) + ', ' +
                str(actual_coordinate[1]) + ')'
            )

    """
    This test projects a coordinate that is 600m east and 400m south from the
    projection origin. If the scale is 100m to 1cm, then we should expect
    an offset of 6cm, 4cm from the canvas origin. In this example, the canvas
    origin is the top-left, inset by 1cm.
    """
    def test_build_crs_to_canvas_transformer(self):
        wgs84_crs = pyproj.CRS.from_epsg(4326)
        british_crs = pyproj.CRS.from_epsg(27700)

        coordinate_to_project = GeoCoordinate(55.862777, -4.260919, wgs84_crs)
        expected_canvas_coordinates = CanvasCoordinate(
            CanvasUnit.from_cm(1+6),
            CanvasUnit.from_cm(1+4)
        ).pt

        origin_for_geo = GeoCoordinate(
            258000,
            666000,
            british_crs
        )
        origin_for_canvas = CanvasCoordinate(
            CanvasUnit.from_cm(1),
            CanvasUnit.from_cm(1)
        )

        # 100 meters for every centimeter
        geo_to_canvas_scale = GeoCanvasScale(
            100,
            CanvasUnit.from_cm(1)
        )

        transformation_func = build_crs_to_canvas_transformer(
            crs=british_crs,
            data_crs=wgs84_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas
        )
        self.assert_coordinates_are_close(
            transformation_func(*coordinate_to_project.tuple),
            expected_canvas_coordinates
        )

        # Repeat the same test, but this time without data_crs:
        transformation_func = build_crs_to_canvas_transformer(
            crs=british_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas
        )
        coordinate_to_project = GeoCoordinate(258600, 665600, british_crs)
        self.assert_coordinates_are_close(
            transformation_func(*coordinate_to_project.tuple),
            expected_canvas_coordinates
        )

        # Repeat the same test, but this time with a `rotation` of 90 degrees:
        transformation_func = build_crs_to_canvas_transformer(
            crs=british_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas,
            rotation=math.pi/2
        )
        coordinate_to_project = GeoCoordinate(258600, 665600, british_crs)
        self.assert_coordinates_are_close(
            transformation_func(*coordinate_to_project.tuple),
            CanvasCoordinate(
                CanvasUnit.from_cm(1 - 4),
                CanvasUnit.from_cm(1 + 6)
            ).pt
        )

        # Repeat the same test, but this time with `is_data_yx` set to True:
        transformation_func = build_crs_to_canvas_transformer(
            crs=british_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas,
            is_crs_yx=True
        )
        coordinate_to_project = GeoCoordinate(258600, 665600, british_crs)
        self.assert_coordinates_are_close(
            transformation_func(*coordinate_to_project.tuple),
            CanvasCoordinate(
                CanvasUnit.from_cm(1 - 4),
                CanvasUnit.from_cm(1 - 6)
            ).pt
        )

        # Repeat the same test, but this time with `is_data_yx` set to True:
        transformation_func = build_crs_to_canvas_transformer(
            crs=british_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas,
            is_data_yx=True
        )
        coordinate_to_project = GeoCoordinate(665600, 258600, british_crs)
        self.assert_coordinates_are_close(
            transformation_func(*coordinate_to_project.tuple),
            expected_canvas_coordinates
        )

    """
    This test projects a coordinate that is 600m east and 400m south from the
    projection origin. If the scale is 100m to 1cm, then we should expect
    an offset of 6cm, 4cm from the canvas origin. In this example, the canvas
    origin is the top-left, inset by 1cm.
    """

    def test_build_canvas_to_crs_transformer(self):
        wgs84_crs = pyproj.CRS.from_epsg(4326)
        british_crs = pyproj.CRS.from_epsg(27700)

        coordinate_to_project = GeoCoordinate(55.862777, -4.260919, wgs84_crs)
        expected_canvas_coordinates = CanvasCoordinate(
            CanvasUnit.from_cm(1 + 6),
            CanvasUnit.from_cm(1 + 4)
        ).pt

        origin_for_geo = GeoCoordinate(
            258000,
            666000,
            british_crs
        )
        origin_for_canvas = CanvasCoordinate(
            CanvasUnit.from_cm(1),
            CanvasUnit.from_cm(1)
        )

        # 100 meters for every centimeter
        geo_to_canvas_scale = GeoCanvasScale(
            100,
            CanvasUnit.from_cm(1)
        )

        transformation_func = build_canvas_to_crs_transformer(
            crs=british_crs,
            data_crs=wgs84_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas
        )
        self.assert_coordinates_are_close(
            transformation_func(*expected_canvas_coordinates),
            coordinate_to_project.tuple
        )

        # Repeat the same test, but this time without data_crs:
        transformation_func = build_canvas_to_crs_transformer(
            crs=british_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas
        )
        coordinate_to_project = GeoCoordinate(258600, 665600, british_crs)
        self.assert_coordinates_are_close(
            transformation_func(*expected_canvas_coordinates),
            coordinate_to_project.tuple
        )

        # Repeat the same test, but this time with a `rotation` of 90 degrees:
        transformation_func = build_canvas_to_crs_transformer(
            crs=british_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas,
            rotation=math.pi/2
        )
        coordinate_to_project = GeoCoordinate(258600, 665600, british_crs)
        self.assert_coordinates_are_close(
            transformation_func(*CanvasCoordinate(
                CanvasUnit.from_cm(1 - 4),
                CanvasUnit.from_cm(1 + 6)
            ).pt),
            coordinate_to_project.tuple
        )

        # Repeat the same test, but this time with `is_crs_yx` set to True:
        transformation_func = build_canvas_to_crs_transformer(
            crs=british_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas,
            is_crs_yx=True
        )
        coordinate_to_project = GeoCoordinate(258600, 665600, british_crs)
        self.assert_coordinates_are_close(
            transformation_func(*CanvasCoordinate(
                CanvasUnit.from_cm(1 - 4),
                CanvasUnit.from_cm(1 - 6)
            ).pt),
            coordinate_to_project.tuple
        )

        # Repeat the same test, but this time with `is_data_yx` set to True:
        transformation_func = build_canvas_to_crs_transformer(
            crs=british_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas,
            is_data_yx=True
        )
        coordinate_to_project = GeoCoordinate(665600, 258600, british_crs)
        self.assert_coordinates_are_close(
            transformation_func(*expected_canvas_coordinates),
            coordinate_to_project.tuple
        )
