from typing import Dict
from abc import ABC
from shapely.geometry import Polygon


class OsmPolygon(Polygon, ABC):
    def __init__(self, shell=None, holes=None):
        super().__init__(shell, holes)
        self._osm_tags = {}

    @property
    def osm_tags(self):
        return self._osm_tags

    @osm_tags.setter
    def osm_tags(self, x: Dict[str, str]):
        self._osm_tags = x
