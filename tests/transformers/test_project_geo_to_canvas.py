import pyproj
import unittest

from mapengraver.transformers.project_geo_to_canvas import \
    build_projection_function


class TestProjectGeoToCanvas(unittest.TestCase):
    def test_conversion(self):
        wgs_84_identity_func = build_projection_function()
        assert wgs_84_identity_func(55.855529, -4.232459) == (
            55.855529, -4.232459
        )

        british_grid_func = build_projection_function(
            output_crs=pyproj.CRS.from_epsg(27700)
        )
        print(british_grid_func(55.855529, -4.232459))
        assert british_grid_func(55.855529, -4.232459) == (
            260354.7929476458, 664735.6993417306
        )
