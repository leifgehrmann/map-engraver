from pathlib import Path

import unittest

from cairocffi import ImageSurface
from pyproj import CRS

from map_engraver.canvas import CanvasBuilder
from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data.canvas_geometry.rect import rect
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers_builder import \
    GeoCanvasTransformersBuilder
from map_engraver.data.geotiff.canvas_transform import \
    transform_geotiff_to_crs_within_canvas, \
    build_geotiff_crs_within_canvas_matrix

from osgeo import gdal

from map_engraver.graphicshelper import CairoHelper


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
        input_file = Path(__file__).parent.joinpath('test.tif')
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
        input_file = Path(__file__).parent.joinpath('test.tif')
        output_file = Path(__file__).parent.joinpath(
            'output/build_geotiff_crs_within_canvas_matrix.tif'
        )
        output_png_file = Path(__file__).parent.joinpath('test.png')
        canvas_file = Path(__file__).parent.joinpath(
            'output/build_geotiff_crs_within_canvas_matrix.svg'
        )
        output_file.unlink(missing_ok=True)
        canvas_file.unlink(missing_ok=True)

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
        builder.rotation = 3.14 / 4
        builder.set_data_crs(wgs84_crs)

        transform_geotiff_to_crs_within_canvas(
            input_file, canvas_mask, builder, output_file
        )

        canvas_builder = CanvasBuilder()
        canvas_builder.set_path(canvas_file)
        canvas_builder.set_size(canvas_width, canvas_height)
        canvas = canvas_builder.build()

        surface_matrix = build_geotiff_crs_within_canvas_matrix(
            canvas_mask,
            builder,
            output_file
        )

        canvas.context.set_source_rgba(0, 0, 1, 0.5)
        CairoHelper.draw_polygon(canvas.context, canvas_mask)
        canvas.context.fill()

        canvas.context.save()
        canvas.context.transform(surface_matrix)

        # For sake of simplicity, pretend that we converted the output image
        # from *.tif to *.png.
        surface = ImageSurface.create_from_png(output_png_file.as_posix())
        canvas.context.set_source_surface(surface, 0, 0)
        canvas.context.paint()

        canvas.context.set_source_rgba(0, 1, 0, 0.5)
        CairoHelper.draw_polygon(
            canvas.context,
            rect(
                CanvasBbox(
                    CanvasCoordinate.origin(),
                    CanvasUnit.from_pt(97),
                    CanvasUnit.from_pt(97)
                )
            )
        )
        canvas.context.fill()

        canvas.context.restore()

        canvas.close()

        assert canvas_file.exists()

        with open(canvas_file, 'r') as file:
            data = file.read()
            assert data.find(
                'M 187.351562 -187.5 '
                'L 562.5 187.351562 '
                'L 187.648438 562.5 '
                'L -187.5 187.648438 Z '
                'M 187.351562 -187.5 '
            ) != -1
