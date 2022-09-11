import unittest
from pyproj import CRS
from shapely.geometry import MultiPolygon, Polygon

from map_engraver.data.proj.cylindrical_masks import \
    is_supported_cylindrical_projection, \
    cylindrical_mask, \
    cylindrical_mask_wgs84


class TestCylindricalMasks(unittest.TestCase):
    def test_is_supported_cylindrical_projection_returns_expected(self):
        # Unsupported projections
        unsupported_crs = [
            CRS.from_epsg(4326),
            CRS.from_proj4('+proj=ortho +lon_0=0 +lat_0=0')
        ]
        for crs in unsupported_crs:
            self.assertFalse(is_supported_cylindrical_projection(crs))

        # Supported projections
        supported_crs = [
            CRS.from_proj4('+proj=utm +zone=59 +south')
        ]
        for crs in supported_crs:
            self.assertTrue(is_supported_cylindrical_projection(crs))

    def test_cylindrical_mask_raises_error_for_unsupported_proj(self):
        with self.assertRaises(RuntimeError):
            cylindrical_mask(CRS.from_epsg(4326))

    def test_cylindrical_mask_wgs84_raises_error_for_unsupported_proj(self):
        with self.assertRaises(RuntimeError):
            cylindrical_mask_wgs84(CRS.from_epsg(4326))

        with self.assertRaises(RuntimeError):
            cylindrical_mask_wgs84(CRS.from_proj4('+proj=utm +zone=0 +south'))

    def test_cylindrical_mask_utm(self):
        # UTM should return an empty mask
        utm_crs = CRS.from_proj4('+proj=utm +zone=59 +south')
        assert cylindrical_mask(utm_crs) is None

    def test_cylindrical_mask_wgs84_utm(self):
        # UTM should have "dead-spots".
        utm_crs = CRS.from_proj4('+proj=utm +zone=1 +south')
        utm_multi_polygon = cylindrical_mask_wgs84(utm_crs)
        self._assert_holes(utm_multi_polygon, 1)

        utm_crs = CRS.from_proj4('+proj=utm +zone=15 +south')
        utm_multi_polygon = cylindrical_mask_wgs84(utm_crs)
        self._assert_holes(utm_multi_polygon, 0)

        utm_crs = CRS.from_proj4('+proj=utm +zone=30 +south')
        utm_multi_polygon = cylindrical_mask_wgs84(utm_crs)
        self._assert_holes(utm_multi_polygon, 0)

        utm_crs = CRS.from_proj4('+proj=utm +zone=45 +south')
        utm_multi_polygon = cylindrical_mask_wgs84(utm_crs)
        self._assert_holes(utm_multi_polygon, 0)

        utm_crs = CRS.from_proj4('+proj=utm +zone=60 +south')
        utm_multi_polygon = cylindrical_mask_wgs84(utm_crs)
        self._assert_holes(utm_multi_polygon, 1)

    def _assert_holes(self, multi_polygon: MultiPolygon, holes: int):
        polygon: Polygon = multi_polygon.geoms[0]
        self.assertEqual(len(list(polygon.interiors)), holes)
