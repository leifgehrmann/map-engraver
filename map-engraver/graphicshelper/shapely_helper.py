from shapely.geometry import Point, Polygon, MultiPolygon, LineString, LinearRing, MultiLineString
from shapely.ops import cascaded_union, polygonize, unary_union, linemerge
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

    @staticmethod
    def get_directional_line_strings_from_multipolygon(
            multi_polygon: MultiPolygon,
            min_angle: float,
            max_angle: float
    ) -> MultiLineString:

        multi_line_strings = []

        for geom in multi_polygon.geoms:
            multi_line_strings.append(ShapelyHelper.get_directional_line_strings_from_polygon(geom, min_angle, max_angle))

        return ShapelyHelper.group_multi_line_strings(multi_line_strings)

    @staticmethod
    def get_directional_line_strings_from_polygon(
            polygon: Polygon,
            min_angle: float,
            max_angle: float
    ) -> MultiLineString:
        multi_line_strings = []

        if hasattr(polygon.exterior, 'coords'):
            multi_line_strings.append(
                ShapelyHelper.get_directional_line_strings_from_line_string(
                    LineString(polygon.exterior),
                    min_angle,
                    max_angle
                )
            )
        else:
            return MultiLineString([])

        for interior in polygon.interiors:
            multi_line_strings.append(
                ShapelyHelper.get_directional_line_strings_from_line_string(
                    interior,
                    min_angle,
                    max_angle
                )
            )

        return ShapelyHelper.group_multi_line_strings(multi_line_strings)

    @staticmethod
    def get_directional_line_strings_from_line_string(
            line_string: LineString,
            min_angle: float,
            max_angle: float
    ) -> MultiLineString:
        line_strings = []
        line_string_piece = []
        coordinates = line_string.coords
        coordinates_count = len(coordinates)

        for coord_i in range(coordinates_count):
            coord_a = Point(coordinates[coord_i % (coordinates_count - 1)])
            coord_b = Point(coordinates[(coord_i + 1) % (coordinates_count - 1)])
            angle = ShapelyHelper.get_direction(coord_a, coord_b)
            if ShapelyHelper.is_angle_between_two_angles(angle, min_angle, max_angle):
                line_string_piece.append(coord_a)
            else:
                if len(line_string_piece) > 0:
                    line_string_piece.append(coord_a)
                if len(line_string_piece) >= 2:
                    line_strings.append(LineString(line_string_piece))
                    line_string_piece = []

        if len(line_string_piece) >= 2:
            line_strings.append(LineString(line_string_piece))

        merged_lines = linemerge(line_strings)
        if isinstance(merged_lines, LineString):
            return MultiLineString([merged_lines])
        else:
            return merged_lines

    @staticmethod
    def is_angle_between_two_angles(angle: float, start_angle: float, end_angle: float):
        while start_angle < -math.pi:
            start_angle += math.pi * 2
            end_angle += math.pi * 2
        while angle < start_angle:
            angle += math.pi * 2
        # if start_angle < -math.pi:
        #     offset = (start_angle + math.pi) / (- 2 * math.pi)
        #     start_angle += offset * math.pi * 2
        #     end_angle += offset * math.pi * 2
        # if angle < start_angle:
        #     offset = (angle - start_angle) / (- 2 * math.pi)
        #     angle += offset * math.pi * 2
        return angle < end_angle

    @staticmethod
    def get_direction(start: Point, end: Point) -> float:
        return math.atan2(end.y - start.y, end.x - start.x)

    @staticmethod
    def group_multi_line_strings(multi_line_strings: List[MultiLineString]) -> MultiLineString:
        geoms = []
        for multi_line_string in multi_line_strings:
            if multi_line_string.is_empty:
                continue
            geoms.extend(multi_line_string.geoms)
        return MultiLineString(geoms)

