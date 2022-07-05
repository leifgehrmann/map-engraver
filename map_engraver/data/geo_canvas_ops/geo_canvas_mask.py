from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import transform

from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers_builder import \
    GeoCanvasTransformersBuilder
from map_engraver.data.proj.azimuthal_masks import \
    azimuthal_mask, azimuthal_mask_wgs84


def canvas_mask(
        canvas_bbox: CanvasBbox,
        transformers_builder: GeoCanvasTransformersBuilder
) -> MultiPolygon:
    """
    Returns a MultiPolygon that covers the extent of the CRS projection, and
    the extent of the canvas, in the canvas's coordinate space.

    In other words, it's the intersection of the canvas box and the extent of
    the CRS projection.

    For example, in the case of an orthographic globe projection that is
    centered in the middle of the canvas, it will simply return the extent of
    the globe projection.

    In another example, in the case of a zoomed in projection of the globe, it
    will simply return the extent of the canvas.

    :param canvas_bbox:
    :param transformers_builder:
    :return:
    """
    canvas_polygon = _create_canvas_polygon(canvas_bbox)

    # Todo: Switch mask based on CRS.
    crs_polygon = azimuthal_mask(transformers_builder.crs)
    # Todo: Clone the builder, because we want to ignore data_crs
    crs_to_canvas = transformers_builder.build_crs_to_canvas_transformer()
    crs_polygon = transform(crs_to_canvas, crs_polygon)

    return canvas_polygon.intersection(crs_polygon)


def crs_mask(
        canvas_bbox: CanvasBbox,
        transformers_builder: GeoCanvasTransformersBuilder
) -> MultiPolygon:
    """
    Returns a MultiPolygon that covers the extent of the CRS projection and the
    extent of the canvas, in the CRS's own coordinate space.

    :param canvas_bbox:
    :param transformers_builder:
    :return:
    """
    canvas_polygon = _create_canvas_polygon(canvas_bbox)
    # Todo: Clone the builder, because we want to ignore data_crs
    canvas_to_crs = transformers_builder.build_canvas_to_crs_transformer()
    canvas_polygon = transform(canvas_to_crs, canvas_polygon)

    # Todo: Switch mask based on CRS.
    crs_polygon = azimuthal_mask(transformers_builder.crs)

    return canvas_polygon.intersection(crs_polygon)


def wgs84_mask(
        canvas_bbox: CanvasBbox,
        transformers_builder: GeoCanvasTransformersBuilder
) -> MultiPolygon:
    """
    Returns a MultiPolygon that covers the extent of the CRS projection and the
    extent of the canvas, in the WGS-84 coordinate space.

    This is useful for culling datasets to fit within a canvas.

    :param canvas_bbox:
    :param transformers_builder:
    :return:
    """
    canvas_polygon = _create_canvas_polygon(canvas_bbox)
    # Todo: Clone the builder, because we want to set the CRS to WGS-84
    canvas_to_crs = transformers_builder.build_canvas_to_crs_transformer()
    canvas_polygon = transform(canvas_to_crs, canvas_polygon)

    # Todo: Switch mask based on CRS.
    crs_polygon = azimuthal_mask_wgs84(transformers_builder.crs)

    return canvas_polygon.intersection(crs_polygon)


def _create_canvas_polygon(canvas_bbox: CanvasBbox) -> Polygon:
    pos = canvas_bbox.pos
    width = canvas_bbox.width
    height = canvas_bbox.height
    return Polygon([
        (pos.x, pos.y),
        (pos.x + width, pos.y),
        (pos.x + width, pos.y + height),
        (pos.x, pos.y + height),
        (pos.x, pos.y),
    ])
