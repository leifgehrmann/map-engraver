from math import sin, cos

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
        rotation: float = 0,
        is_crs_yx: bool = False,
        is_data_yx: bool = False,
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
    :param rotation: Rotates coordinates around the canvas origin. Units are in
                     radians.
    :param is_crs_yx: If true, the transform method will treat projected
                      coordinates as northing/easting instead of
                      easting/northing.
                      This is useful when using the WGS 84 projection which
                      uses northing/easting. Most projections use
                      easting/northing.
    :param is_data_yx: If true, the transform method will swap the coordinates
                       as y, x instead of x, y before projecting to the canvas.
                       This is useful if you have WGS 84 data that is encoded
                       as longitude, latitude, but do not want to re-encode the
                       data as latitude, longitude.
    :return: A transformation function.
    """
    data_transformer: Optional[pyproj.Transformer] = None
    if data_crs is not None:
        data_transformer = pyproj.Transformer.from_proj(
            data_crs,
            crs
        )
    transformed_origin_for_geo = pyproj.Transformer \
        .from_proj(origin_for_geo.crs, crs) \
        .transform(*origin_for_geo.tuple)
    scale_factor = scale.geo_units / scale.canvas_units.pt

    def projection(x: float, y: float) -> Tuple[float, float]:
        coord = (x, y)
        # Flip the original coordinate data.
        if is_data_yx:
            coord = (y, x)

        # Transform the coordinate data to the projected CRS to use on canvas.
        if data_transformer is not None:
            coord = data_transformer.transform(*coord)

        # Translate to position relative to the specified geographic origin.
        coord = (
            coord[0] - transformed_origin_for_geo[0],
            coord[1] - transformed_origin_for_geo[1]
        )

        # Flip the projected coordinate data.
        if is_crs_yx:
            coord = coord[1], coord[0]

        # Rotate relative to specified canvas origin.
        coord = (
                coord[0] * cos(rotation) + coord[1] * sin(rotation),
                coord[1] * cos(rotation) - coord[0] * sin(rotation)
        )

        # Scale and translate relative to the specified canvas origin.
        # The y-coordinate is inverted because the coordinate space in computer
        # graphics is inverted.
        return (
            coord[0] / scale_factor + origin_for_canvas.x.pt,
            coord[1] / -scale_factor + origin_for_canvas.y.pt
        )

    return projection


def build_canvas_to_crs_transformer(
        crs: pyproj.CRS,
        scale: GeoCanvasScale,
        origin_for_geo: GeoCoordinate,
        origin_for_canvas: CanvasCoordinate = CanvasCoordinate.origin(),
        data_crs: Optional[pyproj.CRS] = None,
        rotation: float = 0,
        is_crs_yx: bool = False,
        is_data_yx: bool = False
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
    :param rotation: Un-rotates coordinates around the canvas origin. Units are
                     in radians.
    :param is_crs_yx: If true, the transform method will treat projected
                      coordinates as northing/easting instead of
                      easting/northing.
                      This is useful when using the WGS 84 projection which
                      uses northing/easting. Most projections use
                      easting/northing.
    :param is_data_yx: If true, the transform method will swap the coordinates
                       as y, x instead of x, y after un-projecting to the
                       canvas.
                       This is useful if you want to have WGS 84 data that is
                       encoded as longitude, latitude, but do not want to
                       re-encode the data as latitude, longitude.
    :return: A transformation function.
    """
    inverse_data_transformer: Optional[pyproj.Transformer] = None
    if data_crs is not None:
        inverse_data_transformer = pyproj.Transformer.from_proj(
            crs,
            data_crs,
        )
    transformed_origin_for_geo = pyproj.Transformer \
        .from_proj(origin_for_geo.crs, crs) \
        .transform(*origin_for_geo.tuple)
    scale_factor = scale.geo_units / scale.canvas_units.pt

    def projection(x: float, y: float) -> Tuple[float, float]:
        # Un-translate and un-scale relative to the specified canvas origin.
        # The y-coordinate is inverted because the coordinate space in computer
        # graphics is inverted.
        coord = (
            (x - origin_for_canvas.x.pt) * scale_factor,
            (y - origin_for_canvas.y.pt) * -scale_factor
        )
        # Un-rotate relative to specified canvas origin.
        coord = (
            coord[0] * cos(-rotation) + coord[1] * sin(-rotation),
            coord[1] * cos(-rotation) - coord[0] * sin(-rotation)
        )
        # Un-flip northing/easting to the CRS's original easting/northing axis.
        if is_crs_yx:
            coord = (coord[1], coord[0])
        # Un-translate to position relative to the specified geographic origin.
        coord = (
            coord[0] + transformed_origin_for_geo[0],
            coord[1] + transformed_origin_for_geo[1],
        )

        # Inverse-transform the projected data to the data CRS.
        if inverse_data_transformer is not None:
            coord = inverse_data_transformer.transform(*coord)

        if is_data_yx:
            coord = (coord[1], coord[0])

        return coord

    return projection
