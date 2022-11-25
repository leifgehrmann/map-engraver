import math
from pathlib import Path

import unittest

from PIL import Image
from pyproj import CRS

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data.canvas_geometry.rect import rect
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.geo_canvas_ops.geo_canvas_scale import GeoCanvasScale
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers_builder import \
    GeoCanvasTransformersBuilder
from map_engraver.data.geotiff.canvas_transform import \
    transform_geotiff_to_crs_within_canvas, \
    build_geotiff_crs_within_canvas_matrix

from osgeo import gdal

from map_engraver.drawable.geometry.polygon_drawer import PolygonDrawer
from map_engraver.drawable.images.bitmap import Bitmap


class TestCanvasTransform(unittest.TestCase):
    def setUp(self):
        Path(__file__).parent.joinpath('output/') \
            .mkdir(parents=True, exist_ok=True)

    def test_transform_geotiff_to_crs_within_canvas_invalid(self):
        input_file = Path(__file__).parent.joinpath('invalid.tif')
        output_file = Path(__file__).parent.joinpath(
            'output/transform_geotiff_to_crs_within_canvas_invalid.tif'
        )

        canvas_width = CanvasUnit.from_px(500)
        canvas_height = CanvasUnit.from_px(500)
        canvas_mask = rect(CanvasBbox(
            CanvasCoordinate.origin(),
            canvas_width,
            canvas_height
        ))

        wgs84_crs = CRS.from_epsg(4326)
        builder = GeoCanvasTransformersBuilder()
        builder.set_scale_and_origin_from_coordinates_and_crs(
            wgs84_crs,
            GeoCoordinate(0, 0, wgs84_crs),
            GeoCoordinate(1, 1, wgs84_crs),
            CanvasCoordinate.from_px(0, 0),
            CanvasCoordinate.from_px(1, 1)
        )
        builder.set_data_crs(wgs84_crs)

        with self.assertRaisesRegex(
                RuntimeError,
                'not recognized as a supported file format.'
        ):
            transform_geotiff_to_crs_within_canvas(
                input_file, canvas_mask, builder, output_file
            )

    def test_transform_geotiff_to_crs_within_canvas(self):
        input_file = Path(__file__).parent.joinpath('scotland_hillshade.tif')
        output_file = Path(__file__).parent.joinpath(
            'output/transform_geotiff_to_crs_within_canvas.tif'
        )
        output_file.unlink(missing_ok=True)

        canvas_width = CanvasUnit.from_px(500)
        canvas_height = CanvasUnit.from_px(500)
        canvas_mask = rect(CanvasBbox(
            CanvasCoordinate.origin(),
            canvas_width,
            canvas_height
        ))

        crs = CRS.from_proj4('+proj=utm +zone=30')
        wgs84_crs = CRS.from_epsg(4326)
        builder = GeoCanvasTransformersBuilder()
        builder.set_scale_and_origin_from_coordinates_and_crs(
            crs,
            GeoCoordinate(54.9, -3.1, wgs84_crs),
            GeoCoordinate(54.0, -3.1, wgs84_crs),
            CanvasCoordinate.from_px(canvas_width.px / 2, canvas_height.px),
            CanvasCoordinate.from_px(canvas_width.px / 2, 0)
        )
        builder.set_data_crs(wgs84_crs)

        transform_geotiff_to_crs_within_canvas(
            input_file, canvas_mask, builder, output_file
        )

        self.assertTrue(output_file.exists())
        dataset = gdal.Open(output_file.as_posix(), gdal.GA_ReadOnly)
        dataset_projection = dataset.GetProjection()
        self.assertTrue(
            'PROJCS["WGS 84 / UTM zone 30N"' in dataset_projection
        )
        dataset_geo_transform = dataset.GetGeoTransform()
        self.assertEqual(
            (
                443445.1461688044, 1451.3333723590088, 0.0,
                6083668.242004135, 0.0, -1451.3333723590156
            ),
            dataset_geo_transform
        )

    def test_build_geotiff_crs_within_canvas_matrix(self):
        input_tif_file = Path(__file__).parent.joinpath(
            'scotland_hillshade.tif'
        )
        output_dir = Path(__file__).parent.joinpath('output')
        output_tif_file = output_dir.joinpath(
            'build_geotiff_crs_within_canvas_matrix.tif'
        )
        output_png_file = output_dir.joinpath(
            'build_geotiff_crs_within_canvas_matrix.png'
        )
        canvas_file = Path(__file__).parent.joinpath(
            'output/build_geotiff_crs_within_canvas_matrix.svg'
        )
        output_tif_file.unlink(missing_ok=True)
        output_png_file.unlink(missing_ok=True)
        canvas_file.unlink(missing_ok=True)

        canvas_width = CanvasUnit.from_px(200)
        canvas_height = CanvasUnit.from_px(170)
        canvas_mask = rect(CanvasBbox(
            CanvasCoordinate.origin(),
            canvas_width,
            canvas_height
        ))
        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(canvas_file)
        canvas_builder.set_size(canvas_width, canvas_height)
        canvas = canvas_builder.build()

        crs = CRS.from_proj4('+proj=utm +zone=30')
        wgs84_crs = CRS.from_epsg(4326)
        builder = GeoCanvasTransformersBuilder()
        builder.set_crs(crs)
        builder.set_scale(GeoCanvasScale(100000, canvas_width))
        builder.set_origin_for_geo(GeoCoordinate(57.3, -4.45, wgs84_crs))
        builder.set_origin_for_canvas(CanvasCoordinate.from_px(
            canvas_width.px / 2,
            canvas_height.px / 2
        ))
        builder.rotation = -math.pi / 8 * 3
        builder.set_data_crs(wgs84_crs)

        # To visualize how the transformation makes the image fit into the
        # canvas, we buffer the canvas by a certain amount to add padding.
        scene_canvas = canvas_mask.buffer(CanvasUnit.from_px(-50).pt)

        # Create the image to display on the map. We also will convert the tiff
        # to png, so we can load it easily in cairocffi.
        transform_geotiff_to_crs_within_canvas(
            input_tif_file,
            scene_canvas,
            builder,
            output_tif_file
        )
        output_bitmap = Image.open(output_tif_file)
        output_bitmap.save(output_png_file)

        surface_matrix = build_geotiff_crs_within_canvas_matrix(
            scene_canvas,
            builder,
            output_tif_file
        )

        canvas.context.save()
        canvas.context.transform(surface_matrix)

        bitmap = Bitmap(output_png_file)
        bitmap.draw(canvas)

        polygon_drawer = PolygonDrawer()
        polygon_drawer.stroke_color = (0, 1, 0, 0.5)
        polygon_drawer.stroke_width = CanvasUnit.from_px(1)
        polygon_drawer.geoms = [rect(
            CanvasBbox(
                CanvasCoordinate.origin(),
                CanvasUnit.from_px(output_bitmap.width),
                CanvasUnit.from_px(output_bitmap.height)
            )
        )]
        polygon_drawer.draw(canvas)

        canvas.context.restore()

        polygon_drawer = PolygonDrawer()
        polygon_drawer.stroke_color = (1, 0, 0, 0.5)
        polygon_drawer.stroke_width = CanvasUnit.from_px(1)
        polygon_drawer.geoms = [scene_canvas]
        polygon_drawer.draw(canvas)

        canvas.close()

        assert canvas_file.exists()

        with open(canvas_file, 'r') as file:
            data = file.read()
            assert data.find(
                'M -0.000432709 -0.000179234 '
                'L 26.999834 0.000401775 '
                'L 26.999823 31.499943 '
                'L 0.0000793665 31.500624 Z '
                'M -0.000432709 -0.000179234'
            ) != -1
            assert data.find(
                'matrix('
                '1.094261,-2.64178,2.64178,1.094261,18.938447,82.311553'
                ')'
            ) != -1
