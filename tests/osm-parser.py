#!/user/bin/env python3

import math
import cairocffi as cairo
import osmparser
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString
from shapely.ops import cascaded_union
from typing import Union, List, Tuple

filePath = '../../antique-map/data/osm/DonaldsonsCollege.osm'

osm_map = osmparser.Map()
osm_map.add_osm_file(filePath)

# get buildings
buildings = {
    way_ref: way for
    way_ref, way in
    osm_map.ways.items() if
    ("building" in way.tags)
}

buildings_rel = {
    relation_ref: relation for
    relation_ref, relation in
    osm_map.relations.items() if
    ("building" in relation.tags)
}

barrier = {
    way_ref: way for
    way_ref, way in
    osm_map.ways.items() if
    ("barrier" in way.tags)
}

water = {
    way_ref: way for
    way_ref, way in
    osm_map.ways.items() if
    ("waterway" in way.tags and
     way.tags["waterway"] == "riverbank")
}

natural_water = {
    way_ref: way for
    way_ref, way in
    osm_map.ways.items() if
    ("natural" in way.tags and
     way.tags["natural"] == "water")
}

# get multi polygon buildings = {}

min_lat = 55.94454
min_lon = -3.23028
max_lat = 55.95252
max_lon = -3.21659

# Coordinates should be transformed from the OSM parser
WIDTH, HEIGHT = 4560, 4560

surface = cairo.PDFSurface("output/example.pdf", WIDTH, HEIGHT)
ctx = cairo.Context(surface)

ctx.scale(WIDTH, HEIGHT)  # Normalizing the canvas

pat = cairo.LinearGradient(0.0, 0.0, 0.0, 1.0)
pat.add_color_stop_rgba(1, 0.7, 0, 0, 0.5)  # First stop, 50% opacity
pat.add_color_stop_rgba(0, 0.9, 0.7, 0.2, 1)  # Last stop, 100% opacity


def transform_node(node: Tuple[float, float]):
    return transform_coordinate(node[0], node[1])


def transform_coordinate(lon, lat):
    x = (lon - min_lon) / (max_lon - min_lon)
    y = 1 - ((lat - min_lat) / (max_lat - min_lat))
    return x, y


def draw_relation_way(osmmap: osmparser.map, relation: osmparser.Relation):
    for member in relation.members:
        if member.type == osmparser.MemberTypes.WAY:
            way_nodes = osmmap.get_nodes_for_way(member.ref)
            if member.role == "inner":
                way_nodes = reversed(way_nodes)

            start = True
            for node in way_nodes:
                x = (node.lon - min_lon) / (max_lon - min_lon)
                y = 1 - ((node.lat - min_lat) / (max_lat - min_lat))
                if start:
                    ctx.move_to(x, y)
                else:
                    ctx.line_to(x, y)
                start = False

    ctx.fill()


def draw_way(osmmap: osmparser.map, way: osmparser.Way):
    way_nodes = osmmap.get_nodes_for_way(way.id)
    start = True
    for node in way_nodes:
        x = (node.lon - min_lon) / (max_lon - min_lon)
        y = 1 - ((node.lat - min_lat) / (max_lat - min_lat))
        if start:
            ctx.move_to(x, y)
        else:
            ctx.line_to(x, y)

        start = False
    ctx.stroke()


def draw_line_string(line_string: LineString):
    start = True
    for x, y in line_string.coords:
        if start:
            ctx.move_to(x, y)
        else:
            ctx.line_to(x, y)

        start = False
    ctx.stroke()


def draw_line_string_segmented(line_string: LineString):
    old_x = line_string.coords[len(line_string.coords) - 1][0]
    old_y = line_string.coords[len(line_string.coords) - 1][1]

    for x, y in line_string.coords:
        angle = math.atan2(y - old_y, x - old_x)
        ctx.set_source_rgb((angle + math.pi) / (math.pi * 2), 0, 0)

        ctx.line_to(x, y)

        old_x = x
        old_y = y

        ctx.stroke()

        ctx.move_to(old_x, old_y)
    ctx.stroke()


def draw_polygon(polygon_to_draw: Polygon):
    start = True
    if hasattr(polygon_to_draw.exterior, 'coords'):
        for x, y in polygon_to_draw.exterior.coords:
            if start:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)

            start = False

    for interior in polygon_to_draw.interiors:
        start = True
        for x, y in interior.coords:
            if start:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)

            start = False

    ctx.stroke()


def draw_multipolygon(multipolygon: MultiPolygon):
    index = 0
    for geom in multipolygon.geoms:
        draw_polygon(geom)
        index += 1
    ctx.stroke()


def draw_way_stroke(osmmap: osmparser.map, way: osmparser.Way):
    way_nodes = osmmap.get_nodes_for_way(way.id)
    start = True
    for node in way_nodes:
        x = (node.lon - min_lon) / (max_lon - min_lon)
        y = 1 - ((node.lat - min_lat) / (max_lat - min_lat))
        if start:
            ctx.move_to(x, y)
        else:
            ctx.line_to(x, y)

        start = False
    ctx.stroke()


def get_line_strings_from_line_string(line_string: LineString, min_angle, max_angle) -> List[LineString]:
    line_strings = []
    line_string_piece = []
    coordinates = line_string.coords
    coordinates_count = len(coordinates)

    for coord_i in range(coordinates_count):
        coord_a = coordinates[coord_i % (coordinates_count - 1)]
        coord_b = coordinates[(coord_i + 1) % (coordinates_count - 1)]
        angle = math.atan2(coord_b[1] - coord_a[1], coord_b[0] - coord_a[0])
        if min_angle <= angle <= max_angle:
            line_string_piece.append(coord_a)
        else:
            if len(line_string_piece) > 0:
                line_string_piece.append(coord_a)
            if len(line_string_piece) >= 2:
                line_strings.append(LineString(line_string_piece))
                line_string_piece = []

    if len(line_string_piece) >= 2:
        line_strings.append(LineString(line_string_piece))

    return line_strings


def get_line_strings_from_polygon(polygon_to_read: Polygon, min_angle, max_angle) -> List[LineString]:
    line_strings = []

    if hasattr(polygon_to_read.exterior, 'coords'):
        line_strings.extend(get_line_strings_from_line_string(polygon_to_read.exterior, min_angle, max_angle))
    else:
        return []

    for interior in polygon_to_read.interiors:
        line_strings.extend(get_line_strings_from_line_string(interior, min_angle, max_angle))

    return line_strings


def get_line_strings_from_multipolygon(multi_polygon: MultiPolygon, min_angle, max_angle) -> List[LineString]:
    line_strings = []

    for geom in multi_polygon.geoms:
        line_strings.extend(get_line_strings_from_polygon(geom, min_angle, max_angle))

    return line_strings


def unionize_polygon_array(polygons: List[Polygon]) -> List[Union[Polygon, MultiPolygon]]:
    count = len(polygons)
    if count <= 1:
        return polygons

    polygons_clone = polygons[:]

    index_a = 0
    while index_a < count - 1:
        index_b = index_a + 1
        while index_b < count:
            a = polygons_clone[index_a]
            b = polygons_clone[index_b]
            if a.intersects(b):
                polygons_clone[index_a] = cascaded_union([a, b])
                del polygons_clone[index_b]
                count -= 1
                index_b = index_a + 1
            else:
                index_b += 1
        index_a += 1

    return polygons_clone


buildings_poly = list(map((lambda x: osmparser.Convert.way_to_polygon(osm_map, x, transform_node)), buildings.values()))
rel_buildings_poly = list(
    map((lambda x: osmparser.Convert.relation_to_polygon(osm_map, x, transform_node)), buildings_rel.values()))
buildings_poly.extend(rel_buildings_poly)

reduced_buildings_poly = unionize_polygon_array(buildings_poly)

water_poly = list(map((lambda x: osmparser.Convert.way_to_polygon(osm_map, x, transform_node)), water.values()))
reduced_water_poly = unionize_polygon_array(water_poly)

natural_water_poly = list(
    map((lambda x: osmparser.Convert.way_to_polygon(osm_map, x, transform_node)), natural_water.values()))
reduced_natural_water_poly = unionize_polygon_array(natural_water_poly)

ctx.set_source_rgb(0, 0, 0)
ctx.set_line_width(0.0005)
for polygon in reduced_buildings_poly:
    if isinstance(polygon, MultiPolygon):
        draw_multipolygon(polygon)
    elif isinstance(polygon, Polygon):
        draw_polygon(polygon)

ctx.set_source_rgb(0, 0, 0)
ctx.set_line_width(0.0001)
for way_ref, way in barrier.items():
    draw_way_stroke(osm_map, way)

for i in range(0, 20):
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(0.0001)
    for polygon in reduced_water_poly:
        if isinstance(polygon, MultiPolygon):
            draw_multipolygon(polygon)
        elif isinstance(polygon, Polygon):
            draw_polygon(polygon)
    for polygon_i in range(len(reduced_water_poly)):
        reduced_water_poly[polygon_i] = reduced_water_poly[polygon_i].buffer(-0.0005 * math.sqrt(i), cap_style=3,
                                                                             join_style=cairo.LINE_JOIN_MITER,
                                                                             mitre_limit=1)

for i in range(0, 20):
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(0.0001)
    for polygon in natural_water_poly:
        if isinstance(polygon, MultiPolygon):
            draw_multipolygon(polygon)
        elif isinstance(polygon, Polygon):
            draw_polygon(polygon)
    for polygon_i in range(len(natural_water_poly)):
        natural_water_poly[polygon_i] = natural_water_poly[polygon_i].buffer(-0.0005 * math.sqrt(i),
                                                                             cap_style=cairo.LINE_CAP_SQUARE,
                                                                             join_style=cairo.LINE_JOIN_MITER,
                                                                             mitre_limit=1)

ctx.set_line_width(0.0015)
ctx.set_line_cap(cairo.LINE_CAP_BUTT)
for polygon in reduced_buildings_poly:
    polygon = polygon.buffer(-0.0005, cap_style=cairo.LINE_CAP_BUTT, join_style=cairo.LINE_JOIN_BEVEL, mitre_limit=10)
    lss = []
    if isinstance(polygon, MultiPolygon):
        lss = get_line_strings_from_multipolygon(polygon, -math.pi / 6 * 2, math.pi / 6)
    elif isinstance(polygon, Polygon):
        lss = get_line_strings_from_polygon(polygon, -math.pi / 6 * 4, math.pi / 6)
    for ls in lss:
        if ls is not None and isinstance(ls, LineString):
            if ls.length > 0.001:
                draw_line_string(ls)

ctx.set_line_width(0.0005)
q = 0
for polygon in reduced_buildings_poly:
    q += 1
    for i in range(-125, 250):  # Can be optimised
        line = LineString([(0, i * 4 / 1000), (1, 0.5 + i * 4 / 1000)])
        lines = line.intersection(polygon)
        if isinstance(lines, MultiLineString):
            for sub_line in lines.geoms:
                if isinstance(sub_line, LineString):
                    draw_line_string(sub_line)
        elif isinstance(lines, LineString):
            draw_line_string(lines)

surface.flush()
surface.finish()
