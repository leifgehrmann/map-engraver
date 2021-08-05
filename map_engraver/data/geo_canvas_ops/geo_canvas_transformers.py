import pyproj
from typing import Tuple, Callable, Optional

from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.data.geo.geo_coordinate import GeoCoordinate
from map_engraver.data.geo_canvas_ops.geo_canvas_scale import GeoCanvasScale


def build_transformer(
        # The Coordinate Reference System for plotting coordinate data onto
        # the canvas.
        crs: pyproj.CRS,

        # Controls the scale that things on the map will appear in. For
        # example, the number of meters per centimeter.
        scale: GeoCanvasScale,

        # Controls where the map should point to. If `origin_for_canvas` is the
        # default, this geographic coordinate appear on the top-left corner of
        # the canvas.
        origin_for_geo: GeoCoordinate,

        # Controls where on the canvas the origin should correspond to (Useful
        # if your map has margins on the side of the map). Defaults to the
        # top-left corner of the canvas.
        origin_for_canvas: CanvasCoordinate = CanvasCoordinate.origin(),

        # The Coordinate Reference System for the input data. For example, if
        # your data is longitude/latitude data, you will want to set the
        # `data_crs` as `pyproj.CRS.from_epsg(4326)`.
        data_crs: Optional[pyproj.CRS] = None,
) -> Callable[[float, float], Tuple[float, float]]:
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
