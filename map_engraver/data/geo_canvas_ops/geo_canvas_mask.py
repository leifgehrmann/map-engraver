from shapely.geometry import MultiPolygon

from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.data.geo_canvas_ops.geo_canvas_transformers_builder import \
    GeoCanvasTransformersBuilder


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
    pass


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
    pass


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
    pass
