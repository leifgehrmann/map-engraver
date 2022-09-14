import unittest
from pyproj import CRS

from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.data.canvas_geometry.rect import rect
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.geo_canvas_ops.geo_canvas_mask import \
    canvas_mask, \
    canvas_crs_mask, \
    canvas_wgs84_mask
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers_builder import \
    GeoCanvasTransformersBuilder


class TestMasks(unittest.TestCase):
    def test_canvas_mask(self):
        canvas_size = rect(CanvasBbox.from_pt(-20, 50, 170, 100))
        builder = GeoCanvasTransformersBuilder()
        builder.set_scale_and_origin_from_coordinates_and_crs(
            CRS.from_proj4('+proj=ortho +lon_0=0 +lat_0=0'),
            GeoCoordinate(0, -89, CRS.from_epsg(4326)),
            GeoCoordinate(0, 89, CRS.from_epsg(4326)),
            CanvasCoordinate.from_pt(-20, 100),
            CanvasCoordinate.from_pt(220, 100)
        )

        mask = canvas_mask(canvas_size, builder)
        mask_bounds = mask.bounds
        self.assertAlmostEqual(mask_bounds[0], -20, 4)
        self.assertAlmostEqual(mask_bounds[1], 50, 4)
        self.assertAlmostEqual(mask_bounds[2], 150, 4)
        self.assertAlmostEqual(mask_bounds[3], 150, 4)

    def test_canvas_wgs84_mask(self):
        canvas_size = rect(CanvasBbox.from_pt(-20, 50, 170, 100))
        builder = GeoCanvasTransformersBuilder()
        builder.set_scale_and_origin_from_coordinates_and_crs(
            CRS.from_proj4('+proj=ortho +lon_0=0 +lat_0=0'),
            GeoCoordinate(0, -89, CRS.from_epsg(4326)),
            GeoCoordinate(0, 89, CRS.from_epsg(4326)),
            CanvasCoordinate.from_pt(-20, 100),
            CanvasCoordinate.from_pt(220, 100)
        )

        mask = canvas_wgs84_mask(canvas_size, builder)
        mask_bounds = mask.bounds
        self.assertAlmostEqual(mask_bounds[0], -24.7818, 4)
        self.assertAlmostEqual(mask_bounds[1], -89.9973, 4)
        self.assertAlmostEqual(mask_bounds[2], 24.7818, 4)
        self.assertAlmostEqual(mask_bounds[3], 27.2961, 4)

    def test_canvas_crs_mask(self):
        canvas_size = rect(CanvasBbox.from_pt(-20, 50, 170, 100))
        builder = GeoCanvasTransformersBuilder()
        builder.set_scale_and_origin_from_coordinates_and_crs(
            CRS.from_proj4('+proj=ortho +lon_0=0 +lat_0=0'),
            GeoCoordinate(0, -89, CRS.from_epsg(4326)),
            GeoCoordinate(0, 89, CRS.from_epsg(4326)),
            CanvasCoordinate.from_pt(-20, 100),
            CanvasCoordinate.from_pt(220, 100)
        )

        mask = canvas_crs_mask(canvas_size, builder)
        mask_bounds = mask.bounds
        self.assertAlmostEqual(mask_bounds[0], -6377165.5788417, 4)
        self.assertAlmostEqual(mask_bounds[1], -2657152.324517375, 4)
        self.assertAlmostEqual(mask_bounds[2], 2657152.324517375, 4)
        self.assertAlmostEqual(mask_bounds[3], 2657152.324517375, 4)

    def test_functions_for_crs_with_unknown_mask(self):
        canvas_size = rect(CanvasBbox.from_pt(-20, 50, 170, 100))
        builder = GeoCanvasTransformersBuilder()
        builder.set_scale_and_origin_from_coordinates_and_crs(
            CRS.from_proj4('+proj=nzmg +lat_0=-41 +lon_0=173 +x_0=0 +y_0=0'),
            GeoCoordinate(-29.291, 157.079, CRS.from_epsg(4326)),
            GeoCoordinate(-38.475, 179.384, CRS.from_epsg(4326)),
            CanvasCoordinate.from_pt(-20, 100),
            CanvasCoordinate.from_pt(220, 100)
        )

        mask = canvas_crs_mask(canvas_size, builder)
        mask_bounds = mask.bounds
        self.assertAlmostEqual(mask_bounds[0], 807922.8624918363, 4)
        self.assertAlmostEqual(mask_bounds[1], 6280382.27413151, 4)
        self.assertAlmostEqual(mask_bounds[2], 2483045.0799831273, 4)
        self.assertAlmostEqual(mask_bounds[3], 7265748.284420505, 4)

        mask = canvas_wgs84_mask(canvas_size, builder)
        self.assertIsNone(mask)
