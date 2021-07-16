import pyproj
from typing import Tuple, Callable

from mapengraver.canvas.canvas_unit import CanvasUnit


def build_projection_function(
        input_crs: pyproj.CRS = pyproj.CRS.from_epsg(4326),
        output_crs: pyproj.CRS = pyproj.CRS.from_epsg(4326),
        output_origin: Tuple[float, float] = (0, 0),
        canvas_origin: Tuple[float, float] = (0, 0),
        output_scale: float = 1,
        canvas_scale: CanvasUnit = CanvasUnit(1),
        inverse: bool = False
) -> Callable[[float, float], Tuple[float, float]]:
    geo_projection = pyproj.Transformer.from_proj(
        input_crs,
        output_crs
    )
    translate = (output_origin[0] - canvas_origin[0],
                 output_origin[1] - canvas_origin[1])
    scale = output_scale / canvas_scale.pt

    if inverse:
        geo_projection = pyproj.Transformer.from_proj(
            output_crs,
            input_crs
        )

        def inv_projection(x: float, y: float) -> Tuple[float, float]:
            coord = (x / scale + translate[0], y / scale + translate[1])
            return geo_projection.transform(coord[0], coord[1])

        return inv_projection
    else:
        geo_projection = pyproj.Transformer.from_proj(
            input_crs,
            output_crs
        )

        def projection(x: float, y: float) -> Tuple[float, float]:
            coord = geo_projection.transform(x, y)
            translated = (coord[0] - translate[0], coord[1] - translate[1])
            return translated[0] * scale, translated[1] * scale

        return projection
