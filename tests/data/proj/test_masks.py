import unittest
from pyproj import CRS
from shapely.geometry import MultiPolygon

from map_engraver.data.proj.masks import crs_mask, wgs84_mask


class TestMasks(unittest.TestCase):
    def test_crs_mask_correct_projections_are_selected(self):
        # WGS 84
        self.assertIsInstance(crs_mask(CRS.from_epsg(4326)), MultiPolygon)
        # Azimuthal
        self.assertIsInstance(
            crs_mask(CRS.from_proj4('+proj=ortho')), MultiPolygon
        )
        # Cylindrical
        self.assertIsNone(crs_mask(CRS.from_epsg(32601)))
        # Unknown
        self.assertIsNone(crs_mask(CRS.from_epsg(27200)))

    def test_wgs84_mask_correct_projections_are_selected(self):
        # WGS 84
        self.assertIsInstance(wgs84_mask(CRS.from_epsg(4326)), MultiPolygon)
        # Azimuthal
        self.assertIsInstance(
            wgs84_mask(CRS.from_proj4('+proj=ortho')), MultiPolygon
        )
        # Cylindrical
        self.assertIsInstance(wgs84_mask(CRS.from_epsg(32601)), MultiPolygon)
        # Unknown
        self.assertIsNone(wgs84_mask(CRS.from_epsg(27200)))
