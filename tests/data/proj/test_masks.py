import pyproj
from pathlib import Path

import unittest
from pyproj import CRS
from shapely import ops
from shapely.geometry import Polygon

from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu

from map_engraver.canvas import CanvasBuilder
from map_engraver.data import geo_canvas_ops
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.proj.masks import orthographic_mask, _binary_search_edge_wgs84
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer


class TestMasks(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

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
        # print(_binary_search_edge_wgs84(crs))
        print(orthographic_mask(crs))

    def test_orthographic_masks_at_45_north(self):
        pass

    def test_orthographic_masks_at_north_pole(self):
        pass

    def test_orthographic_masks_at_anti_meridian(self):
        pass


    def test_only_fill(self):
        path = Path(__file__).parent.joinpath(
            'output/mask.svg'
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)
        canvas_builder.set_size(Cu.from_px(400), Cu.from_px(220))

        canvas = canvas_builder.build()

        wgs84_crs = pyproj.CRS.from_epsg(4326)

        origin_for_geo = GeoCoordinate(
            0,
            0,
            wgs84_crs
        )
        origin_for_canvas = CanvasCoordinate(
            Cu.from_px(200),
            Cu.from_px(110)
        )

        # 1 pixel for every degree
        geo_to_canvas_scale = geo_canvas_ops.GeoCanvasScale(
            1,
            Cu.from_px(1)
        )

        crs = CRS.from_proj4('+proj=ortho +lat_0=0')
        # crs = CRS.from_proj4('+proj=ortho +lon_0=180 +lat_0=0')
        # crs = CRS.from_proj4('+proj=ortho +lon_0=180 +lat_0=0.1')
        # crs = CRS.from_proj4('+proj=ortho +lat_0=20')
        crs = CRS.from_proj4('+proj=ortho +lat_0=90')
        crs = CRS.from_proj4('+proj=ortho +lat_0=5')
        # crs = CRS.from_proj4('+proj=geos +h=35785831.0 +lon_0=-60 +sweep=x')
        # crs = CRS.from_proj4('+proj=geos +h=35785831.0 +lon_0=-160 +sweep=x')
        # crs = CRS.from_proj4('+proj=nsper +h=3000000 +lat_0=-20 +lon_0=-60')
        # crs = CRS.from_proj4('+proj=nsper +h=8000000 +lat_0=-20 +lon_0=-60')
        # crs = CRS.from_proj4('+proj=nsper +h=3000000 +lat_0=-20 +lon_0=145')
        # crs = CRS.from_proj4('+proj=nsper +h=3000000 +lat_0=-80 +lon_0=145')
        # crs = CRS.from_proj4('+proj=tpers +h=5500000 +lat_0=40')
        # crs = CRS.from_proj4('+proj=tpers +h=5500000 +lat_0=-40')
        # crs = CRS.from_proj4('+proj=tpers +h=5500000 +lat_0=30 +lon_0=-120 +tilt=30')
        multi_polygon = orthographic_mask(crs, resolution=400)
        multi_polygon = ops.transform(lambda x, y: (y, x), multi_polygon)

        transformation_func = geo_canvas_ops.build_transformer(
            crs=wgs84_crs,
            data_crs=wgs84_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas
        )

        multi_polygon = ops.transform(transformation_func, multi_polygon)

        domain = Polygon([(-180, -90), (180, -90), (180, 90), (-180, 90)])
        domain = ops.transform(transformation_func, domain)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0, 0, 1)
        polygon_drawer.geoms = [domain]
        polygon_drawer.draw(canvas)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0, 1, 0)
        polygon_drawer.geoms = [multi_polygon, Polygon([(-180, -90), (180, -90), (180, -90)])]
        polygon_drawer.draw(canvas)

        canvas.close()

    # Confirm all points are valid coordinates
    # Confirm the number of geoms in the multi polygon
    # Confirm the width
    # Confirm the height
