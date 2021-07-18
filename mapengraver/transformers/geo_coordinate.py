import pyproj
from typing import Tuple


class GeoCoordinate:
    x: float
    y: float
    crs: pyproj.CRS

    def __init__(self, x: float, y: float, crs: pyproj.CRS):
        self.x = x
        self.y = y
        self.crs = crs

    @property
    def xy(self) -> Tuple[float, float]:
        return self.x, self.y
