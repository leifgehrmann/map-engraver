import pyproj
from typing import Tuple, Callable

from mapengraver.canvas.canvas_unit import CanvasUnit


def build_projection_function(
        input_crs: pyproj.CRS = pyproj.CRS.from_epsg(4326),
        output_crs: pyproj.CRS = pyproj.CRS.from_epsg(4326),
        output_origin: Tuple[float, float] = (0, 0),
        canvas_origin: Tuple[float, float] = (0, 0),
        output_scale: float = 1,
        canvas_scale: CanvasUnit = CanvasUnit(1)
) -> Callable[[float, float], Tuple[float, float]]:
    my_function = pyproj.Transformer.from_proj(
        input_crs,
        output_crs
    )
    return lambda x, y: my_function.transform(x, y)
