from typing import List, Dict

import re

from pathlib import Path

import unittest
from pyproj import CRS
from shapely.geometry import MultiPolygon, MultiLineString, Polygon
from shapely.ops import transform

from map_engraver.canvas import Canvas, CanvasBuilder
from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data.canvas_geometry.rect import rounded_rect
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.geo_canvas_ops.geo_canvas_mask import \
    canvas_wgs84_mask, \
    canvas_mask
from map_engraver.data.geo_canvas_ops.geo_canvas_scale import GeoCanvasScale
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers_builder import \
    GeoCanvasTransformersBuilder
from map_engraver.data.osm_shapely_ops.homogenize import \
    geoms_to_multi_line_string, geoms_to_multi_polygon
from map_engraver.data.osm_shapely_ops.transform import \
    transform_interpolated_euclidean
from map_engraver.data.proj.masks import wgs84_mask
from map_engraver.drawable.geometry.line_drawer import LineDrawer
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer
from tests.e2e.projection_rendering.world_objects import \
    get_world_map, \
    get_flight_paths


class TestGeoCanvasRendering(unittest.TestCase):
    canvas_margin = 20

    crs_width = 400
    crs_height = 400
    crs_bbox = CanvasBbox.from_size_px(
        canvas_margin, canvas_margin,
        crs_width, crs_height
    )

    wgs84_width = 360
    wgs84_height = 180
    wgs84_bbox = CanvasBbox.from_size_px(
        canvas_margin * 2 + crs_width, canvas_margin,
        wgs84_width, wgs84_height
    )

    whole_canvas_bbox = CanvasBbox.from_size_px(
        0, 0,
        canvas_margin * 3 + crs_width + wgs84_width,
        crs_height + canvas_margin * 2
    )

    sea_color = (0/255, 101/255, 204/255)
    land_color = (183/255, 218/255, 158/255)
    line_color = (1, 0, 0, 0.75)

    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_geo_canvas_mask_outputs_expected_polygons(self):
        for case in self.get_test_cases():
            proj4_str = case['proj4']

            crs = CRS.from_proj4(proj4_str)

            transformer_builder = GeoCanvasTransformersBuilder()
            transformer_builder.set_scale_and_origin_from_coordinates_and_crs(
                crs,
                case['geo_a'],
                case['geo_b'],
                case['canvas_a'],
                case['canvas_b']
            )
            transformer_builder.set_data_crs(CRS.from_epsg(4326))

            # We will now create a mask to filter the world objects we want to
            # render.
            canvas_polygon = canvas_mask(
                rounded_rect(self.crs_bbox, CanvasUnit.from_px(50)),
                transformer_builder
            )
            wgs84_polygon = wgs84_mask(
                crs
            )
            canvas_wgs84_polygon = canvas_wgs84_mask(
                rounded_rect(self.crs_bbox, CanvasUnit.from_px(50)),
                transformer_builder
            )

            world_map = get_world_map()
            world_map = geoms_to_multi_polygon(
                world_map.intersection(canvas_wgs84_polygon)
            )
            flight_paths = get_flight_paths()
            flight_paths = geoms_to_multi_line_string(
                flight_paths.intersection(canvas_wgs84_polygon)
            )

            canvas = self.build_canvas(proj4_str)
            self.draw_crs(
                canvas,
                canvas_polygon,
                transformer_builder,
                world_map,
                flight_paths
            )
            self.draw_wgs84(
                canvas,
                wgs84_polygon,
                canvas_wgs84_polygon,
                world_map,
                flight_paths
            )
            canvas.close()

    def build_canvas(self, name: str) -> Canvas:
        name = re.sub(r'[^0-9A-Za-z_-]', '', name)
        path = Path(__file__).parent.joinpath(
            'output/geo_canvas_rendering_%s.svg' % name
        )
        path.unlink(missing_ok=True)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(path)

        canvas_builder.set_size(
            self.whole_canvas_bbox.width, self.whole_canvas_bbox.height
        )

        return canvas_builder.build()

    def draw_crs(
            self,
            canvas: Canvas,
            canvas_polygon: MultiPolygon,
            transformer_builder: GeoCanvasTransformersBuilder,
            world_map_wgs84: MultiPolygon,
            flight_paths_wgs84: MultiLineString
    ):
        wgs84_to_canvas = transformer_builder.build_crs_to_canvas_transformer()

        world_map_canvas = transform_interpolated_euclidean(
            wgs84_to_canvas,
            world_map_wgs84
        )
        flight_paths_canvas = transform_interpolated_euclidean(
            wgs84_to_canvas,
            flight_paths_wgs84
        )

        # Render the polygons
        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = self.sea_color
        polygon_drawer.geoms = [canvas_polygon]
        polygon_drawer.draw(canvas)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = self.land_color
        polygon_drawer.geoms = [world_map_canvas]
        polygon_drawer.draw(canvas)

        polygon_drawer = LineDrawer()
        polygon_drawer.stroke_color = self.line_color
        polygon_drawer.geoms = [flight_paths_canvas]
        polygon_drawer.draw(canvas)

    def draw_wgs84(
            self,
            canvas,
            mask_wgs84,
            canvas_mask_wgs84,
            world_map_wgs84: MultiPolygon,
            flight_paths_wgs84: MultiLineString
    ):
        # Generate a polygon that represents the full range.
        domain_wgs84 = Polygon(
            [(-90, -180), (90, -180), (90, 180), (-90, 180)]
        )

        wgs84_transformer = GeoCanvasTransformersBuilder()
        wgs84_transformer.set_crs(CRS.from_epsg(4326))
        wgs84_transformer.set_origin_for_canvas(self.wgs84_bbox.min_pos)
        wgs84_transformer.set_origin_for_geo(
            GeoCoordinate(90, -180, CRS.from_epsg(4326))
        )
        wgs84_transformer.set_scale(GeoCanvasScale(1, CanvasUnit.from_px(1)))
        wgs84_transformer.set_is_crs_yx(True)
        wgs84_to_canvas = wgs84_transformer.build_crs_to_canvas_transformer()

        mask_canvas = transform(wgs84_to_canvas, mask_wgs84)
        canvas_mask_canvas = transform(wgs84_to_canvas, canvas_mask_wgs84)
        world_map_canvas = transform(wgs84_to_canvas, world_map_wgs84)
        flight_paths_canvas = transform(wgs84_to_canvas, flight_paths_wgs84)
        domain_canvas = transform(wgs84_to_canvas, domain_wgs84)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0, 0, 0)
        polygon_drawer.geoms = [domain_canvas]
        polygon_drawer.draw(canvas)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0.2, 0.2, 0.2)
        polygon_drawer.geoms = [mask_canvas]
        polygon_drawer.draw(canvas)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = self.sea_color
        polygon_drawer.geoms = [canvas_mask_canvas]
        polygon_drawer.draw(canvas)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = self.land_color
        polygon_drawer.geoms = [world_map_canvas]
        polygon_drawer.draw(canvas)

        polygon_drawer = LineDrawer()
        polygon_drawer.stroke_color = self.line_color
        polygon_drawer.geoms = [flight_paths_canvas]
        polygon_drawer.draw(canvas)

    def get_test_cases(self) -> List[Dict]:
        return [
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=0',
                'geo_a': GeoCoordinate(0, -70, CRS.from_epsg(4326)),
                'geo_b': GeoCoordinate(0, 70, CRS.from_epsg(4326)),
                'canvas_a': CanvasCoordinate(
                    self.crs_bbox.min_pos.x,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                ),
                'canvas_b': CanvasCoordinate(
                    self.crs_bbox.min_pos.x + self.crs_bbox.width,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                )
            },
            {
                'proj4': '+proj=ortho +lon_0=180 +lat_0=0',
                'geo_a': GeoCoordinate(0, 150, CRS.from_epsg(4326)),
                'geo_b': GeoCoordinate(0, -150, CRS.from_epsg(4326)),
                'canvas_a': CanvasCoordinate(
                    self.crs_bbox.min_pos.x,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                ),
                'canvas_b': CanvasCoordinate(
                    self.crs_bbox.min_pos.x + self.crs_bbox.width,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                )
            },
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=40',
                'geo_a': GeoCoordinate(40, -40, CRS.from_epsg(4326)),
                'geo_b': GeoCoordinate(40, 20, CRS.from_epsg(4326)),
                'canvas_a': CanvasCoordinate(
                    self.crs_bbox.min_pos.x,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                ),
                'canvas_b': CanvasCoordinate(
                    self.crs_bbox.min_pos.x + self.crs_bbox.width,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                )
            },
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=90',
                'geo_a': GeoCoordinate(10, -180, CRS.from_epsg(4326)),
                'geo_b': GeoCoordinate(10, 0, CRS.from_epsg(4326)),
                'canvas_a': CanvasCoordinate(
                    self.crs_bbox.min_pos.x,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                ),
                'canvas_b': CanvasCoordinate(
                    self.crs_bbox.min_pos.x + self.crs_bbox.width,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                )
            },
            {
                'proj4': '+proj=ortho +lon_0=0 +lat_0=-90',
                'geo_a': GeoCoordinate(-10, -180, CRS.from_epsg(4326)),
                'geo_b': GeoCoordinate(-10, 0, CRS.from_epsg(4326)),
                'canvas_a': CanvasCoordinate(
                    self.crs_bbox.min_pos.x,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                ),
                'canvas_b': CanvasCoordinate(
                    self.crs_bbox.min_pos.x + self.crs_bbox.width,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                )
            },
            {
                'proj4': '+proj=geos +h=35785831.0 +lon_0=-160 +sweep=x',
                'geo_a': GeoCoordinate(0, -140, CRS.from_epsg(4326)),
                'geo_b': GeoCoordinate(0, 160, CRS.from_epsg(4326)),
                'canvas_a': CanvasCoordinate(
                    self.crs_bbox.min_pos.x,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                ),
                'canvas_b': CanvasCoordinate(
                    self.crs_bbox.min_pos.x + self.crs_bbox.width,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                )
            },
            {
                'proj4': '+proj=utm +zone=30 +north',
                'geo_a': GeoCoordinate(45, -10, CRS.from_epsg(4326)),
                'geo_b': GeoCoordinate(45, 56, CRS.from_epsg(4326)),
                'canvas_a': CanvasCoordinate(
                    self.crs_bbox.min_pos.x,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                ),
                'canvas_b': CanvasCoordinate(
                    self.crs_bbox.min_pos.x + self.crs_bbox.width,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                )
            },
            {
                'proj4': '+proj=utm +zone=31 +north',
                'geo_a': GeoCoordinate(45, -10, CRS.from_epsg(4326)),
                'geo_b': GeoCoordinate(45, 56, CRS.from_epsg(4326)),
                'canvas_a': CanvasCoordinate(
                    self.crs_bbox.min_pos.x,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                ),
                'canvas_b': CanvasCoordinate(
                    self.crs_bbox.min_pos.x + self.crs_bbox.width,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                )
            },
            {
                'proj4': '+proj=utm +zone=29 +north',
                'geo_a': GeoCoordinate(55, -15, CRS.from_epsg(4326)),
                'geo_b': GeoCoordinate(55, 6, CRS.from_epsg(4326)),
                'canvas_a': CanvasCoordinate(
                    self.crs_bbox.min_pos.x,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                ),
                'canvas_b': CanvasCoordinate(
                    self.crs_bbox.min_pos.x + self.crs_bbox.width,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                )
            },
            {
                'proj4': '+proj=utm +zone=1 +north',
                'geo_a': GeoCoordinate(45, -10, CRS.from_epsg(4326)),
                'geo_b': GeoCoordinate(45, 56, CRS.from_epsg(4326)),
                'canvas_a': CanvasCoordinate(
                    self.crs_bbox.min_pos.x,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                ),
                'canvas_b': CanvasCoordinate(
                    self.crs_bbox.min_pos.x + self.crs_bbox.width,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                )
            },
            {
                'proj4': '+proj=utm +zone=16 +north',
                'geo_a': GeoCoordinate(9, -85, CRS.from_epsg(4326)),
                'geo_b': GeoCoordinate(9, -75, CRS.from_epsg(4326)),
                'canvas_a': CanvasCoordinate(
                    self.crs_bbox.min_pos.x,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                ),
                'canvas_b': CanvasCoordinate(
                    self.crs_bbox.min_pos.x + self.crs_bbox.width,
                    self.crs_bbox.min_pos.y + self.crs_bbox.height / 2
                )
            },
        ]
