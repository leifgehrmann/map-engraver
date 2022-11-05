from pathlib import Path

import cairocffi
from shapely.geometry import Polygon

from osgeo import gdal

from map_engraver.data.geo.geo_coordinate_transformers import \
    transform_geo_coordinates_to_new_crs
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
    dataset = gdal.Open(output_geotiff.as_posix(), gdal.GA_ReadOnly)
    geo_transform = dataset.GetGeoTransform()
    geotiff_width = geo_transform[1]
    matrix = cairocffi.Matrix()
    matrix.scale(1 / geotiff_width)
    matrix.scale(crs_bounds[2] - crs_bounds[0])
    matrix.translate(crs_bounds[0], crs_bounds[3])

    crs_origin = transform_geo_coordinates_to_new_crs(
        [transformers_builder.origin_for_geo], transformers_builder.crs
    )[0]
    matrix.translate(-crs_origin.x, -crs_origin.y)

    matrix.scale(
        transformers_builder.scale.canvas_units.pt /
        transformers_builder.scale.geo_units
    )

    matrix.rotate(-transformers_builder.rotation)

    matrix.translate(
        -transformers_builder.origin_for_canvas.x.pt,
        -transformers_builder.origin_for_canvas.y.pt
    )

    return matrix
