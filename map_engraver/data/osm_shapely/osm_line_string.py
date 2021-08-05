from typing import Dict
from abc import ABC
from shapely.geometry import LineString


class OsmLineString(LineString, ABC):
    def __init__(self, coordinates=None):
        super().__init__(coordinates)
        self._osm_tags = {}

    @property
    def osm_tags(self):
        return self._osm_tags

    @osm_tags.setter
    def osm_tags(self, x: Dict[str, str]):
        self._osm_tags = x
