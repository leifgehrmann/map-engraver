import pyproj
import unittest

from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.geo_canvas_ops.geo_canvas_scale import GeoCanvasScale
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers_builder import \
    GeoCanvasTransformersBuilder
from tests.data.geo_canvas_ops.test_geo_canvas_transformers import \
    TestGeoCanvasTransformers


class TestGeoCanvasTransformersBuilder(unittest.TestCase):
    def test_setters(self):
        wgs84_crs = pyproj.CRS.from_epsg(4326)
        british_crs = pyproj.CRS.from_epsg(27700)

        builder = GeoCanvasTransformersBuilder()
        builder.set_crs(british_crs)
        builder.set_data_crs(wgs84_crs)
        builder.set_origin_for_geo(GeoCoordinate(325600, 673400, british_crs))
        builder.set_origin_for_canvas(CanvasCoordinate.from_pt(200, 200))
        builder.set_scale(GeoCanvasScale(1000, CanvasUnit.from_pt(100)))

        crs_to_canvas = builder.build_crs_to_canvas_transformer()
        TestGeoCanvasTransformers.assert_coordinates_are_close(
            crs_to_canvas(55.947854, -3.192893),
            (200, 200)
        )
        TestGeoCanvasTransformers.assert_coordinates_are_close(
            crs_to_canvas(55.956836, -3.193169),
            (200, 100)
        )

        canvas_to_crs = builder.build_canvas_to_crs_transformer()
        TestGeoCanvasTransformers.assert_coordinates_are_close(
            canvas_to_crs(200, 200),
            (55.947854, -3.192893)
        )
        TestGeoCanvasTransformers.assert_coordinates_are_close(
            canvas_to_crs(200, 100),
            (55.956836, -3.193169)
        )

    def test_set_scale_and_origin_from_coordinates_and_crs(self):
        wgs84_crs = pyproj.CRS.from_epsg(4326)
        british_crs = pyproj.CRS.from_epsg(27700)

        builder = GeoCanvasTransformersBuilder()
        builder.set_data_crs(wgs84_crs)

        with self.assertRaises(Exception):
            # Test that the method fails if the input geoCoordinates cannot be
            # projected to the british_crs.
            builder.set_scale_and_origin_from_coordinates_and_crs(
                british_crs,
                GeoCoordinate(1800, 900, wgs84_crs),
                GeoCoordinate(1800, 900, wgs84_crs),
                CanvasCoordinate.from_pt(0, 0),
                CanvasCoordinate.from_pt(400, 400),
            )

        builder.set_scale_and_origin_from_coordinates_and_crs(
            british_crs,
            GeoCoordinate(327600, 671400, british_crs),
            GeoCoordinate(323600, 675400, british_crs),
            CanvasCoordinate.from_pt(0, 0),
            CanvasCoordinate.from_pt(400, 400),
        )

        crs_to_canvas = builder.build_crs_to_canvas_transformer()
        TestGeoCanvasTransformers.assert_coordinates_are_close(
            crs_to_canvas(55.947854, -3.192893),
            (200, 200)
        )
        TestGeoCanvasTransformers.assert_coordinates_are_close(
            crs_to_canvas(55.956836, -3.193169),
            (200, 100)
        )

        canvas_to_crs = builder.build_canvas_to_crs_transformer()
        TestGeoCanvasTransformers.assert_coordinates_are_close(
            canvas_to_crs(200, 200),
            (55.947854, -3.192893)
        )
        TestGeoCanvasTransformers.assert_coordinates_are_close(
            canvas_to_crs(200, 100),
            (55.956836, -3.193169)
        )

    def test_not_calling_any_setters(self):
        builder = GeoCanvasTransformersBuilder()

        with self.assertRaises(Exception):
            builder.build_crs_to_canvas_transformer()

        with self.assertRaises(Exception):
            builder.build_canvas_to_crs_transformer()

