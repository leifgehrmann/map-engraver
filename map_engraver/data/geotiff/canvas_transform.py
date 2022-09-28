from pathlib import Path

from shapely.geometry import Polygon

from osgeo import gdal

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
