from shapely.geometry import LineString as ShapelyLineString
from typing import Dict


class LineString(ShapelyLineString):

    def __init__(self, coordinates=None):
        super(LineString, self).__init__(coordinates=coordinates)
        self.osm_tags = {}

    @staticmethod
    def from_shapely(line_string: ShapelyLineString) -> 'LineString':
        return LineString(coordinates=line_string.coords)

    def set_osm_tags(self, osm_tags: Dict[str, str]) -> None:
        self.osm_tags = osm_tags

    def get_osm_tags(self) -> Dict[str, str]:
        return self.osm_tags
