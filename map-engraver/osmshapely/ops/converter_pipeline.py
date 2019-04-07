from typing import List

from osmparser import Map, Way, Relation, Node
from osmshapely.ops import ShapelyClipper, ShapelyConverter, ShapelyTransformer
from osmshapely import Point as OsmPoint
from osmshapely import LineString as OsmLineString
from osmshapely import Polygon as OsmPolygon
from osmshapely.ops.shapely_converter import WayToPolygonError


class ConverterPipeline:

    def __init__(self, osmmap: Map):
        self.osmmap = osmmap
        self.converter = ShapelyConverter(osmmap)
        self.clipper = ShapelyClipper()
        self.transformer = ShapelyTransformer()

    def set_clipper(self, clipper: ShapelyClipper):
        self.clipper = clipper

    def set_transformer(self, transformer: ShapelyTransformer):
        self.transformer = transformer

    def nodes_to_points(self, nodes: List[Node]) -> List[OsmPoint]:
        osm_points = []
        for node in nodes:
            point = self.converter.node_to_point(node)
            points = self.clipper.clip_point(point)
            points = self.transformer.transform_list(points)
            for point in points:
                osm_point = OsmPoint.from_shapely(point)
                osm_point.set_osm_tags(node.tags)
                osm_points.append(osm_point)
        return osm_points

    def ways_to_line_strings(self, ways: List[Way]) -> List[OsmLineString]:
        osm_line_strings = []
        for way in ways:
            line_string = self.converter.way_to_linestring(way)
            line_strings = self.clipper.clip_line_string(line_string)
            line_strings = self.transformer.transform_list(line_strings)
            for line_string in line_strings:
                osm_line_string = OsmLineString.from_shapely(line_string)
                osm_line_string.set_osm_tags(way.tags)
                osm_line_strings.append(osm_line_string)
        return osm_line_strings

    def ways_to_polygons(self, ways: List[Way]) -> List[OsmPolygon]:
        osm_polygons = []
        for way in ways:
            try:
                polygon = self.converter.way_to_polygon(way)
                polygons = self.clipper.clip_polygon(polygon)
                polygons = self.transformer.transform_list(polygons)
                for polygon in polygons:
                    osm_polygon = OsmPolygon.from_shapely(polygon)
                    osm_polygon.set_osm_tags(way.tags)
                    osm_polygons.append(osm_polygon)
            except WayToPolygonError:
                continue
        return osm_polygons

    def relations_to_polygons(
            self,
            relations: List[Relation]
    ) -> List[OsmPolygon]:
        osm_polygons = []
        for relation in relations:
            try:
                polygon = self.converter.relation_to_polygon(relation)
                if polygon is None:
                    continue
                polygons = self.clipper.clip_polygon(polygon)
                polygons = self.transformer.transform_list(polygons)
                for polygon in polygons:
                    osm_polygon = OsmPolygon.from_shapely(polygon)
                    osm_polygon.set_osm_tags(relation.tags)
                    osm_polygons.append(osm_polygon)
            except WayToPolygonError:
                continue
        return osm_polygons
