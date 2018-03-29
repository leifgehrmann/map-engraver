from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import cascaded_union
from typing import Union, List
import math


class ShapelyHelper:

    debug = False

    @staticmethod
    def point_distance(p1: Point, p2: Point):
        return math.hypot(p2.x - p1.x, p2.y - p1.y)

    @staticmethod
    def unionize_polygon_array(polygons: List[Polygon]) -> List[Polygon]:
        count = len(polygons)
        if count <= 1:
            return polygons

        polygons_clone = polygons[:]

        index_a = 0
        if ShapelyHelper.debug:
            print("unionizing polygons")
        while index_a < count - 1:
            if ShapelyHelper.debug and index_a % 10 == 0:
                print("unionizing " + index_a + " polygon")
            index_b = index_a + 1
            while index_b < count:
                a = polygons_clone[index_a]
                b = polygons_clone[index_b]

                if a.intersects(b):
                    osm_tags_union = []
                    if hasattr(a, 'osm_tags'):
                        osm_tags_union.append(a.osm_tags)
                    if hasattr(b, 'osm_tags'):
                        osm_tags_union.append(b.osm_tags)
                    if hasattr(a, 'osm_tags_joined'):
                        osm_tags_union += a.osm_tags_joined
                    if hasattr(b, 'osm_tags_joined'):
                        osm_tags_union += b.osm_tags_joined
                    polygons_clone[index_a] = cascaded_union([a, b])
                    polygons_clone[index_a].osm_tags_union = osm_tags_union
                    del polygons_clone[index_b]
                    count -= 1
                    index_b = index_a + 1
                else:
                    index_b += 1
            index_a += 1

        # Convert all Multipolygons into polygons since they aren't that useful
        if ShapelyHelper.debug:
            print("Converting multipolygons to polygons")
        index = 0
        count = len(polygons_clone)
        while index < count - 1:
            element = polygons_clone[index]
            if isinstance(element, MultiPolygon):
                for sub_polygon in element.geoms:
                    polygons_clone.append(sub_polygon)
                del polygons_clone[index]
                count -= 1
                index -= 1
            index += 1

        return polygons_clone
