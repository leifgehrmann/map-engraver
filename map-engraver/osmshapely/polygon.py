from abc import ABC
from shapely.geometry import Polygon as ShapelyPolygon
from typing import Dict


class Polygon(ShapelyPolygon, ABC):

    def __init__(self, shell=None, holes=None):
        super(Polygon, self).__init__(shell=shell, holes=holes)
        self.tags = {}

    @staticmethod
    def from_shapely(polygon: ShapelyPolygon) -> 'Polygon':
        return Polygon(shell=polygon.exterior, holes=polygon.interiors)

    def set_tags(self, tags: Dict[str, str]) -> None:
        self.tags = tags

    def get_tags(self) -> Dict[str, str]:
        return self.tags
