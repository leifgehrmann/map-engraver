from shapely.geometry import Point as ShapelyPoint
from typing import Optional, Dict


class Point(ShapelyPoint):

    def __init__(self, x: float, y: float, z: Optional[float] = None):
        if z is None:
            super(Point, self).__init__(x, y)
        else:
            super(Point, self).__init__(x, y, z)
        self.osm_tags = {}

    @staticmethod
    def from_shapely(point: ShapelyPoint) -> 'Point':
        if point.has_z:
            return Point(point.x, point.y, point.z)
        else:
            return Point(point.x, point.y)

    def set_osm_tags(self, osm_tags: Dict[str, str]) -> None:
        self.osm_tags = osm_tags

    def get_osm_tags(self) -> Dict[str, str]:
        return self.osm_tags
