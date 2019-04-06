from abc import ABC
from shapely.geometry import Polygon as ShapelyPolygon
from typing import Dict


class Polygon(ShapelyPolygon, ABC):

    def __init__(self, shell=None, holes=None):
        super(Polygon, self).__init__(shell=shell, holes=holes)
        self.osm_tags = {}

    @staticmethod
    def from_shapely(polygon: ShapelyPolygon) -> 'Polygon':
        return Polygon(shell=polygon.exterior, holes=polygon.interiors)

    def set_osm_tags(self, osm_tags: Dict[str, str]) -> None:
        self.osm_tags = osm_tags

    def get_osm_tags(self) -> Dict[str, str]:
        return self.osm_tags
