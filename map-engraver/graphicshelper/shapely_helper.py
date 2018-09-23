from shapely.geometry import Point, Polygon, MultiPolygon, LineString, LinearRing
from shapely.ops import cascaded_union, polygonize, unary_union
from typing import List, Callable
import math
from random import random


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

    @staticmethod
    def interpolate_line_string(line_string: LineString, distance: float):
        coordinates = line_string.coords
        coordinates_count = len(coordinates)
        new_coordinates = []
        for i in range(coordinates_count):
            coord_a = coordinates[i]
            coord_b = coordinates[(i + 1) % coordinates_count]
            short_linestring = LineString([coord_a, coord_b])
            for d in range(int(math.ceil(short_linestring.length / distance))):
                new_coordinates.append(short_linestring.interpolate(d * distance))
        return LineString(new_coordinates)

    @staticmethod
    def interpolate_polygon(polygon: Polygon, distance: float):
        exterior_linestring = LineString(polygon.exterior.coords)
        complex_exterior = ShapelyHelper.interpolate_line_string(exterior_linestring, distance)
        complex_interior = []
        for interior in polygon.interiors:
            complex_interior.append(ShapelyHelper.interpolate_line_string(LineString(interior.coords), distance))
        return Polygon(complex_exterior, complex_interior)

    @staticmethod
    def convert_non_simple_polygon_to_multi_polygon(polygon: Polygon) -> MultiPolygon:
        polygon_exterior = polygon.exterior
        multi_line_string = polygon_exterior.intersection(polygon_exterior)
        polygons = polygonize(multi_line_string)
        multi_polygon = MultiPolygon(polygons)

        for polygon_interior in polygon.interiors:
            multi_polygon = multi_polygon.difference(Polygon(polygon_interior))

        if isinstance(multi_polygon, Polygon):
            multi_polygon = MultiPolygon([multi_polygon])

        return multi_polygon

    @staticmethod
    def linestring_noise_random_square(line_string: LineString, distance: float) -> LineString:
        new_line_string_coords = []
        for x, y in line_string.coords:
            new_line_string_coords.append(
                (random() * distance - distance / 2 + x, random() * distance - distance / 2 + y))
        return LineString(new_line_string_coords)

    @staticmethod
    def polygon_noise(
            polygon: Polygon,
            line_string_noise_function: Callable[[LineString, float], LineString],
            distance: float
    ) -> MultiPolygon:
        exterior_noisy_linestring = line_string_noise_function(LineString(polygon.exterior.coords), distance)
        exterior_polygons = []
        if not exterior_noisy_linestring.is_simple or not LinearRing(exterior_noisy_linestring.coords).is_valid:
            exterior_noisy_multi_polygon = ShapelyHelper.convert_non_simple_polygon_to_multi_polygon(
                Polygon(exterior_noisy_linestring)
            )
            for exterior_noisy_multi_polygon_geom in exterior_noisy_multi_polygon.geoms:
                exterior_polygons.append(exterior_noisy_multi_polygon_geom)
        else:
            exterior_polygons.append(Polygon(exterior_noisy_linestring.coords))

        # Merge exterior polygons into one
        exterior_polygons = unary_union(exterior_polygons)

        for interior in polygon.interiors:
            exterior_polygons = exterior_polygons.difference(
                ShapelyHelper.polygon_noise(
                    Polygon(interior.coords),
                    line_string_noise_function,
                    distance
                )
            )

        if isinstance(exterior_polygons, Polygon):
            exterior_polygons = MultiPolygon([exterior_polygons])

        return exterior_polygons
