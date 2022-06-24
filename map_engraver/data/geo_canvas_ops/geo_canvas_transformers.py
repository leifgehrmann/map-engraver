import pyproj
from typing import Tuple, Callable, Optional

from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.geo_canvas_ops.geo_canvas_scale import GeoCanvasScale


def build_crs_to_canvas_transformer(
        crs: pyproj.CRS,
        scale: GeoCanvasScale,
        origin_for_geo: GeoCoordinate,
        origin_for_canvas: CanvasCoordinate = CanvasCoordinate.origin(),
        data_crs: Optional[pyproj.CRS] = None,
) -> Callable[[float, float], Tuple[float, float]]:
    """
    Returns a transformation function that projects x, y coordinates to
    points on a canvas.

    :param crs: The Coordinate Reference System for plotting coordinate data
                onto the canvas.
    :param scale: Controls the scale that things on the map will appear in. For
                  example, the number of meters per centimeter.
    :param origin_for_geo: Controls where the map should point to. If
                           `origin_for_canvas` is the default, this geographic
                           coordinate appear in the top-left corner of the
                           canvas.
    :param origin_for_canvas: Controls where on the canvas the origin should
                              correspond to (Useful if your map has margins on
                              the side of the map). Defaults to the top-left
                              corner of the canvas.
    :param data_crs: The Coordinate Reference System for the input data. For
                     example, if your data is longitude/latitude data, you will
                     want to set the `data_crs` as
                     `pyproj.CRS.from_epsg(4326)`.
    :return: A transformation function.
    """
    data_transformer: Optional[pyproj.Transformer] = None
    if data_crs is not None:
        data_transformer = pyproj.Transformer.from_proj(
            data_crs,
            crs
        )
    transformed_origin_for_geo = pyproj.Transformer\
        .from_proj(origin_for_geo.crs, crs)\
        .transform(*origin_for_geo.tuple)
    scale_factor = scale.geo_units / scale.canvas_units.pt

    def projection(x: float, y: float) -> Tuple[float, float]:
        if data_transformer is not None:
            coord = data_transformer.transform(x, y)
        else:
            coord = (x, y)
        translated = (
            coord[0] - transformed_origin_for_geo[0],
            coord[1] - transformed_origin_for_geo[1]
        )
        # The y-coordinate is inverted because the coordinate space in computer
        # graphics is inverted.
        return (
            translated[0] / scale_factor + origin_for_canvas.x.pt,
            translated[1] / -scale_factor + origin_for_canvas.y.pt
        )

    return projection


def build_canvas_to_crs_transformer(
        crs: pyproj.CRS,
        scale: GeoCanvasScale,
        origin_for_geo: GeoCoordinate,
        origin_for_canvas: CanvasCoordinate = CanvasCoordinate.origin(),
        data_crs: Optional[pyproj.CRS] = None,
) -> Callable[[float, float], Tuple[float, float]]:
    """
    Returns a transformation function that inverses projected coordinates on a
    canvas into the original data coordinates.

    :param crs: The Coordinate Reference System for plotting coordinate data
                onto the canvas.
    :param scale: Controls the scale that things on the map will appear in. For
                  example, the number of meters per centimeter.
    :param origin_for_geo: Controls where the map should point to. If
                           `origin_for_canvas` is the default, this geographic
                           coordinate appear in the top-left corner of the
                           canvas.
    :param origin_for_canvas: Controls where on the canvas the origin should
                              correspond to (Useful if your map has margins on
                              the side of the map). Defaults to the top-left
                              corner of the canvas.
    :param data_crs: The Coordinate Reference System for the input data. For
                     example, if your data is longitude/latitude data, you will
                     want to set the `data_crs` as
                     `pyproj.CRS.from_epsg(4326)`.
    :return: A transformation function.
    """
    inverse_data_transformer: Optional[pyproj.Transformer] = None
    if data_crs is not None:
        inverse_data_transformer = pyproj.Transformer.from_proj(
            crs,
            data_crs
        )
    transformed_origin_for_geo = pyproj.Transformer\
        .from_proj(origin_for_geo.crs, crs)\
        .transform(*origin_for_geo.tuple)
    scale_factor = scale.geo_units / scale.canvas_units.pt

    def projection(x: float, y: float) -> Tuple[float, float]:
        # The y-coordinate is inverted because the coordinate space in computer
        # graphics is inverted.
        translated = (
            (x - origin_for_canvas.x.pt) * scale_factor,
            (y - origin_for_canvas.y.pt) * -scale_factor
        )
        original_proj = (
            translated[0] + transformed_origin_for_geo[0],
            translated[1] + transformed_origin_for_geo[1],
        )

        if inverse_data_transformer is not None:
            return inverse_data_transformer.transform(*original_proj)
        else:
            return original_proj

    return projection
