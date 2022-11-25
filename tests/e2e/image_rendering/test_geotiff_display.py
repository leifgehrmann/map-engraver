import unittest
from pathlib import Path

from PIL import Image
from pyproj import CRS
from shapely.ops import transform

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.data.canvas_geometry.rect import rect
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.geo_canvas_ops.geo_canvas_mask import canvas_wgs84_mask
from map_engraver.data.geo_canvas_ops.geo_canvas_scale import GeoCanvasScale
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers_builder import \
    GeoCanvasTransformersBuilder
from map_engraver.data.geotiff.canvas_transform import \
    transform_geotiff_to_crs_within_canvas, \
    build_geotiff_crs_within_canvas_matrix
from map_engraver.data.osm import Parser
from map_engraver.data.osm_shapely.natural_coastline import \
    natural_coastline_to_multi_polygon, \
    CoastlineOutputType
from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer
from map_engraver.drawable.images.bitmap import Bitmap
from map_engraver.drawable.images.svg import Svg


class TestGeotiffDisplay(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_geotiff_display(self):
        rel_path = Path(__file__).parent
        output_path = rel_path.joinpath('output/')
        input_osm_path = rel_path.joinpath('scotland_outline.osm')
        input_tif_wgs84_path = rel_path.joinpath('scotland_hillshade.tif')
        output_tif_utm30_path = output_path.joinpath('geotiff_display.tif')
        output_png_utm30_path = output_path.joinpath('geotiff_display.png')
        output_svg_path = output_path.joinpath('geotiff_display.svg')
        output_svg_path.unlink(missing_ok=True)

        # Canvas creation.
        canvas_box = CanvasBbox.from_px(0, 0, 150, 200)
        canvas_polygon = rect(canvas_box)
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(output_svg_path)
        canvas_builder.set_size(canvas_box.width, canvas_box.height)
        canvas = canvas_builder.build()

        # Map projection.
        crs = CRS.from_proj4('+proj=utm +zone=30')
        wgs84_crs = CRS.from_epsg(4326)
        builder = GeoCanvasTransformersBuilder()
        builder.set_crs(crs)
        builder.set_scale(GeoCanvasScale(300000, canvas_box.width))
        builder.set_origin_for_geo(GeoCoordinate(57.5, -4.5, wgs84_crs))
        builder.set_origin_for_canvas(CanvasCoordinate(
            canvas_box.width / 2,
            canvas_box.height / 2
        ))
        builder.rotation = -0.2
        builder.set_data_crs(wgs84_crs)
        wgs84_to_canvas = builder.build_crs_to_canvas_transformer()
        wgs84_mask_geom = canvas_wgs84_mask(canvas_polygon, builder)

        # Project hillshade data.
        transform_geotiff_to_crs_within_canvas(
            input_tif_wgs84_path,
            canvas_polygon,
            builder,
            output_tif_utm30_path
        )
        output_bitmap = Image.open(output_tif_utm30_path)
        output_bitmap.save(output_png_utm30_path)

        surface_matrix = build_geotiff_crs_within_canvas_matrix(
            canvas_polygon,
            builder,
            output_tif_utm30_path
        )

        # Draw Bitmap.
        canvas.context.save()
        canvas.context.transform(surface_matrix)
        bitmap = Bitmap(output_png_utm30_path)
        bitmap.draw(canvas)
        canvas.context.restore()

        # Draw SVG.
        canvas.context.save()
        canvas.context.transform(surface_matrix)
        svg_drawer = Svg(rel_path.joinpath('scotland_poi.svg'))
        svg_drawer.draw(canvas)
        canvas.context.restore()

        # Create coastline data from OSM data.
        osm_map = Parser.parse(input_osm_path)
        coastline_wgs84 = natural_coastline_to_multi_polygon(
            osm_map,
            wgs84_mask_geom.bounds,
            CoastlineOutputType.LAND
        )
        coastline_canvas = transform(wgs84_to_canvas, coastline_wgs84)

        # Draw the coastline
        polygon_drawer = PolygonDrawer()
        polygon_drawer.fill_color = (0, 1, 0, 0.4)
        polygon_drawer.geoms = [coastline_canvas]
        polygon_drawer.draw(canvas)

        canvas.close()
