from typing import Dict
from abc import ABC
from shapely.geometry import Point


class OsmPoint(Point, ABC):
    def __init__(self, *args):
        super().__init__(*args)
        self._osm_tags = {}

    @property
    def osm_tags(self):
        return self._osm_tags

    @osm_tags.setter
    def osm_tags(self, x: Dict[str, str]):
        self._osm_tags = x
