import re

from pathlib import Path

import unittest
from pyproj import CRS
from shapely import ops
from shapely.geometry import MultiPolygon, Polygon

from map_engraver.canvas import Canvas, CanvasBuilder
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit as Cu
from map_engraver.data import geo_canvas_ops
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.osm import Parser
from map_engraver.data.osm_shapely.osm_to_shapely import OsmToShapely
from map_engraver.data.proj.masks import orthographic_mask, \
    orthographic_mask_wgs84
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer
from tests.data.proj.orthographic_cases import get_orthographic_test_cases


class TestOrthographicRendering(unittest.TestCase):
    world_map_path = 'world.osm'
    margin = 20
    orthographic_width = 400
    orthographic_height = 400
    wgs84_width = 360
    wgs84_height = 180

    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_orthographic_mask_outputs_expected_polygons(self):
        for case in get_orthographic_test_cases():
            proj4_str = case['proj4']

            crs = CRS.from_proj4(proj4_str)
            mask = orthographic_mask(crs)
            mask_wgs84 = orthographic_mask_wgs84(crs)

            world_map = self.get_world_map()
            world_map = world_map.intersection(mask_wgs84)

            canvas = self.build_canvas(proj4_str)
            self.draw_orthographic(canvas, crs, mask, world_map)
            self.draw_wgs84(canvas, mask_wgs84, world_map)
            canvas.close()

    def build_canvas(self, name: str) -> Canvas:
        name = re.sub(r'[^0-9A-Za-z_-]', '', name)
        path = Path(__file__).parent.joinpath(
            'output/orthographic_rendering_%s.svg' % name
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)

        canvas_builder.set_size(
            Cu.from_px(
                self.margin * 3 + self.orthographic_width + self.wgs84_width
            ),
            Cu.from_px(
                self.margin * 2 + self.orthographic_height
            )
        )

        return canvas_builder.build()

    def get_world_map(self) -> MultiPolygon:
        path = Path(__file__).parent.joinpath(self.world_map_path)

        osm_map = Parser.parse(path)
        osm_to_shapely = OsmToShapely(osm_map)

        polygons = map(osm_to_shapely.way_to_polygon, osm_map.ways.values())
        return MultiPolygon(polygons)

    def draw_orthographic(
            self,
            canvas: Canvas,
            crs: CRS,
            mask_proj: Polygon,
            world_map_wgs84: MultiPolygon
    ):
        origin_for_geo = GeoCoordinate(0, 0, crs)

        origin_x = Cu.from_px(self.margin + self.orthographic_width / 2)
        origin_y = Cu.from_px(self.margin + self.orthographic_height / 2)
        origin_for_canvas = CanvasCoordinate(origin_x, origin_y)

        # Fit the projected radius as the width of the canvas
        geo_to_canvas_scale = geo_canvas_ops.GeoCanvasScale(
            crs.ellipsoid.semi_major_metre,
            Cu.from_px(self.orthographic_width / 2)
        )

        # Convert the projected mask to the canvas.
        proj_to_canvas = geo_canvas_ops.build_transformer(
            crs=crs,
            data_crs=crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas
        )
        mask_canvas = ops.transform(proj_to_canvas, mask_proj)

        # Convert the world map, from wgs84 to proj to canvas
        wgs84_crs = CRS.from_epsg(4326)
        wgs84_to_canvas = geo_canvas_ops.build_transformer(
            crs=crs,
            data_crs=wgs84_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas
        )
        world_map_canvas = ops.transform(wgs84_to_canvas, world_map_wgs84)

        # Render the polygons
        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0, 0, 1)
        polygon_drawer.geoms = [mask_canvas]
        polygon_drawer.draw(canvas)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0, 1, 0)
        polygon_drawer.geoms = [world_map_canvas]
        polygon_drawer.draw(canvas)

    def draw_wgs84(
            self,
            canvas: Canvas,
            mask_wgs84: MultiPolygon,
            world_map_wgs84: MultiPolygon
    ):
        wgs84_crs = CRS.from_epsg(4326)

        origin_for_geo = GeoCoordinate(
            0,
            0,
            wgs84_crs
        )
        origin_for_canvas = CanvasCoordinate(
            Cu.from_px(self.margin * 2 + self.orthographic_width +
                       self.wgs84_width / 2),
            Cu.from_px(self.margin + self.wgs84_height / 2)
        )

        # 1 pixel for every degree
        geo_to_canvas_scale = geo_canvas_ops.GeoCanvasScale(
            1,
            Cu.from_px(1)
        )

        # Todo: These transformations should be handled by build_transformer.
        mask_wgs84 = ops.transform(lambda x, y: (y, x), mask_wgs84)
        world_map_wgs84 = ops.transform(lambda x, y: (y, x), world_map_wgs84)

        # Generate a polygon that represents the full range.
        domain_wgs84 = Polygon(
            [(-180, -90), (180, -90), (180, 90), (-180, 90)]
        )

        wgs84_to_canvas = geo_canvas_ops.build_transformer(
            crs=wgs84_crs,
            data_crs=wgs84_crs,
            scale=geo_to_canvas_scale,
            origin_for_geo=origin_for_geo,
            origin_for_canvas=origin_for_canvas
        )

        mask_canvas = ops.transform(wgs84_to_canvas, mask_wgs84)
        world_map_canvas = ops.transform(wgs84_to_canvas, world_map_wgs84)
        domain_canvas = ops.transform(wgs84_to_canvas, domain_wgs84)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0, 0, 0)
        polygon_drawer.geoms = [domain_canvas]
        polygon_drawer.draw(canvas)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0, 0, 1)
        polygon_drawer.geoms = [mask_canvas]
        polygon_drawer.draw(canvas)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0, 1, 0)
        polygon_drawer.geoms = [world_map_canvas]
        polygon_drawer.draw(canvas)
