from shapely.geometry import MultiPolygon, LineString, MultiLineString, Polygon
from shapely.geometry.base import BaseGeometry
from typing import List, Optional


class ShapelyClipper:
    """
    Clips geometry based on the passed in geometry
    """

    def __init__(self, clipping_geometry: Optional[BaseGeometry] = None):
        """
        :param clipping_geometry:
            the geometry to apply the intersection of geometry on
        """
        self.clipping_geometry = clipping_geometry

    def clip_line_string(
            self,
            line_string: LineString
    ) -> List[LineString]:
        """
        Returns an array of lineStrings that are a result of intersecting a
        LineString with the clipping geometry.

        :param line_string:
            the LineString to clip
        :return:
            a list of LineStrings that are within the clipping boundary
        """
        if self.clipping_geometry is None:
            return [line_string]

        output = []
        intersected_lines = line_string.intersection(self.clipping_geometry)
        if isinstance(intersected_lines, MultiLineString):
            for sub_line in intersected_lines.geoms:
                if isinstance(sub_line, LineString):
                    output.append(sub_line)
        elif isinstance(intersected_lines, LineString):
            output.append(intersected_lines)
        return output

    def clip_polygon(
            self,
            polygon: Polygon
    ) -> List[Polygon]:
        """
        Returns an array of polygons that are a result of intersecting a
        polygon with the clipping geometry.

        :param polygon:
            the Polygon to clip
        :return:
            a list of Polygons that are within the clipping boundary
        """
        if self.clipping_geometry is None:
            return [polygon]

        output = []
        intersected_polygons = polygon.intersection(self.clipping_geometry)
        if isinstance(intersected_polygons, MultiPolygon):
            for sub_line in intersected_polygons.geoms:
                if isinstance(sub_line, Polygon):
                    output.append(sub_line)
        elif isinstance(intersected_polygons, Polygon):
            output.append(intersected_polygons)
        return output
