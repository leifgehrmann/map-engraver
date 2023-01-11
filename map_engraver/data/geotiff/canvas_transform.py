from pathlib import Path

import cairocffi
from shapely.geometry import Polygon

from PIL import Image
from osgeo import gdal

from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data.geo.geo_coordinate_transformers import \
    transform_geo_coordinate_to_new_crs
from map_engraver.data.geo_canvas_ops.geo_canvas_mask import canvas_crs_mask
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers_builder import \
    GeoCanvasTransformersBuilder


def transform_geotiff_to_crs_within_canvas(
    geotiff: Path,
    canvas_polygon: Polygon,
    transformers_builder: GeoCanvasTransformersBuilder,
    output_geotiff: Path
):
    gdal.UseExceptions()
    dataset = gdal.Open(geotiff.as_posix(), gdal.GA_ReadOnly)
    crs_mask = canvas_crs_mask(canvas_polygon, transformers_builder)
    options = gdal.WarpOptions(
        format='GTiff',
        dstSRS=transformers_builder.crs.to_string(),
        outputBounds=crs_mask.bounds
    )
    gdal.Warp(output_geotiff.as_posix(), dataset, options=options)


def build_geotiff_crs_within_canvas_matrix(
        canvas_polygon: Polygon,
        transformers_builder: GeoCanvasTransformersBuilder,
        output_geotiff: Path
) -> cairocffi.Matrix:
    crs_mask = canvas_crs_mask(canvas_polygon, transformers_builder)
    crs_bounds = crs_mask.bounds

    image = Image.open(output_geotiff.as_posix())
    geotiff_width = image.size[0]

    matrix = cairocffi.Matrix()

    # Convert bitmap coordinate space to CRS coordinate space.
    # 1. Reduce the width of image to "1 unit".
    image_scale_to_unit_scale = cairocffi.Matrix()
    image_scale_to_unit_scale.scale(1 / CanvasUnit.from_px(geotiff_width).pt)
    matrix = matrix * image_scale_to_unit_scale

    # 2. Enlarge the image to be the size of the CRS's mask bounds. The units
    #    will generally be in meters or feet.
    unit_scale_to_crs_scale = cairocffi.Matrix()
    unit_scale_to_crs_scale.scale(crs_bounds[2] - crs_bounds[0])
    matrix = matrix * unit_scale_to_crs_scale

    # 3. Translate the image's top-left coordinate to the coordinate space of
    #    the CRS. Note: We invert for the y-axis because normally on the canvas
    #    the y-axis goes down. But on regular map coordinates, y-axis goes up.
    matrix.x0 += crs_bounds[0]
    matrix.y0 += crs_bounds[3] * -1

    # Next, convert CRS coordinate space to canvas space. Note: We invert for
    # the y-axis because normally on the canvas the y-axis goes down. But on
    # regular map coordinates, y-axis goes up.
    crs_origin = transform_geo_coordinate_to_new_crs(
        transformers_builder.origin_for_geo, transformers_builder.crs
    )
    matrix.x0 += -crs_origin.x
    matrix.y0 += -crs_origin.y * -1

    # Scale to canvas units
    crs_scale_to_canvas_scale = cairocffi.Matrix()
    crs_scale_to_canvas_scale.scale(
        transformers_builder.scale.canvas_units.pt /
        transformers_builder.scale.geo_units
    )
    matrix = matrix * crs_scale_to_canvas_scale

    # Rotate canvas
    canvas_rotate = cairocffi.Matrix()
    canvas_rotate.rotate(
        transformers_builder.rotation
    )
    matrix = matrix * canvas_rotate

    # Translate
    canvas_translate = cairocffi.Matrix()
    canvas_translate.translate(
        transformers_builder.origin_for_canvas.x.pt,
        transformers_builder.origin_for_canvas.y.pt
    )
    matrix = matrix * canvas_translate

    return matrix
