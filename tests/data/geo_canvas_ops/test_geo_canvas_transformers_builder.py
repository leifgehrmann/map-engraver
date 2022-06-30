import pyproj
import unittest

from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.geo_canvas_ops.geo_canvas_scale import GeoCanvasScale
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers_builder import \
    GeoCanvasTransformersBuilder


class TestGeoCanvasTransformersBuilder(unittest.TestCase):
    def test_setters(self):
        wgs84_crs = pyproj.CRS.from_epsg(4326)
        british_crs = pyproj.CRS.from_epsg(27700)

        builder = GeoCanvasTransformersBuilder()
        builder.set_crs(british_crs)
        builder.set_data_crs(wgs84_crs)
        builder.set_origin_for_geo(GeoCoordinate(325600, 673400, british_crs))
        builder.set_origin_for_canvas(CanvasCoordinate.from_pt(200, 200))
        builder.set_scale(GeoCanvasScale(100, CanvasUnit.from_pt(100)))
        pass
