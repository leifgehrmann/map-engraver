import unittest
from pyproj import CRS

from map_engraver.data.proj.masks import orthographic_mask, _binary_search_edge_wgs84


class TestMasks(unittest.TestCase):
    def test_orthographic_masks_at_equator(self):
        crs = CRS.from_proj4('+proj=ortho +lat_0=0')
        crs = CRS.from_proj4('+proj=ortho +lon_0=180 +lat_0=0.1')
        # crs = CRS.from_proj4('+proj=ortho +lat_0=20')
        # crs = CRS.from_proj4('+proj=ortho +lat_0=90')
        # crs = CRS.from_proj4('+proj=geos +h=35785831.0 +lon_0=-60 +sweep=x')
        # crs = CRS.from_proj4('+proj=geos +h=35785831.0 +lon_0=-160 +sweep=x')
        # crs = CRS.from_proj4('+proj=nsper +h=3000000 +lat_0=-20 +lon_0=-60')
        # crs = CRS.from_proj4('+proj=nsper +h=3000000 +lat_0=-20 +lon_0=-60')
        # crs = CRS.from_proj4('+proj=nsper +h=3000000 +lat_0=-20 +lon_0=145')
        # crs = CRS.from_proj4('+proj=nsper +h=3000000 +lat_0=-80 +lon_0=145')
        # crs = CRS.from_proj4('+proj=tpers +h=5500000 +lat_0=40')
        # crs = CRS.from_proj4('+proj=tpers +h=5500000 +lat_0=-40')
        # crs = CRS.from_proj4('+proj=tpers +h=5500000 +lat_0=30 +lon_0=-120 +tilt=30')
        print(_binary_search_edge_wgs84(crs))
        print(orthographic_mask(crs))

    def test_orthographic_masks_at_45_north(self):
        pass

    def test_orthographic_masks_at_north_pole(self):
        pass

    def test_orthographic_masks_at_anti_meridian(self):
        pass
