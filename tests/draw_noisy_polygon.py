import math
from typing import List
from random import random, seed
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union
from shapely.ops import polygonize
from shapely.ops import polygonize_full
from shapely import affinity

import cairocffi as cairo

from graphicshelper.cairo_helper import CairoHelper

from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString

surface = cairo.PDFSurface("output/noisy_polygon.pdf", 400, 400)
ctx = cairo.Context(surface)

# seed(6)

def complexify_linestring(linestring: LineString, tolerance: float) -> LineString:
    coords = linestring.coords
    coords_count = len(coords)
    new_coords = []
    for i in range(coords_count):
        coord_a = coords[i]
        coord_b = coords[(i + 1) % coords_count]
        short_linestring = LineString([coord_a, coord_b])
        for d in range(int(math.ceil(short_linestring.length / tolerance))):
            new_coords.append(short_linestring.interpolate(d * tolerance))
    return LineString(new_coords)


def complexify_polygon(polygon: Polygon, tolerance: float) -> Polygon:
    exterior_linestring = LineString(polygon.exterior.coords)
    complex_exterior = complexify_linestring(exterior_linestring, tolerance)
    complex_interior = []
    for interior in polygon.interiors:
        complex_interior.append(complexify_linestring(LineString(interior.coords), tolerance))
    return Polygon(complex_exterior, complex_interior)


# Apply noise to line string here
def apply_noise(linestring: LineString, distance: float) -> LineString:
    new_linestring_coords = []
    for x, y in linestring.coords:
        new_linestring_coords.append((random() * distance - distance / 2 + x, random() * distance - distance / 2 + y))
    return LineString(new_linestring_coords)


def make_polygon_simple(polygon: Polygon) -> MultiPolygon:
    polygon_exterior = polygon.exterior
    multi_line_string = polygon_exterior.intersection(polygon_exterior)
    polygons = polygonize(multi_line_string)
    multi_polygon = MultiPolygon(polygons)

    print(multi_polygon)

    for polygon_interior in polygon.interiors:
        print(polygon_interior)
        multi_polygon = multi_polygon.difference(Polygon(polygon_interior))

    if isinstance(multi_polygon,Polygon):
        multi_polygon = MultiPolygon([multi_polygon])

    return multi_polygon


def polygon_noise(polygon: Polygon, distance: float) -> List[Polygon]:
    exterior_noisy_linestring = apply_noise(LineString(polygon.exterior.coords), distance)
    exterior_polygons = []
    if not exterior_noisy_linestring.is_simple:
        print("NOT SIMPLE")
        exterior_noisy_multi_polygon = make_polygon_simple(Polygon(exterior_noisy_linestring))
        for exterior_noisy_multi_polygon_geom in exterior_noisy_multi_polygon.geoms:
            exterior_polygons.append(exterior_noisy_multi_polygon_geom)
    else:
        exterior_polygons.append(Polygon(exterior_noisy_linestring.coords))

    # Merge exterior polygons into one
    exterior_polygons = unary_union(exterior_polygons)

    for interior in polygon.interiors:
        exterior_polygons = exterior_polygons.difference(polygon_noise(Polygon(interior), distance))

    return exterior_polygons


coordinates = []

for i in range(0, 20 * 10):
    coordinates.append([math.sin(i / 10 * math.pi / 10 * 3) * 200 + 200, math.cos(i / 10 * math.pi / 10) * 200 + 200])

# original data
line_string = LineString(coordinates)

line_string = apply_noise(line_string, 12)
# closed, non-simple
linear_ring = LineString(line_string.coords[:] + line_string.coords[0:1])

if not linear_ring.is_simple:
    multi_line_string = unary_union(linear_ring)
    for polygon in polygonize(multi_line_string):
        print(polygon)
        ctx.set_source_rgba(random(), random(), random(), 1)
        CairoHelper.draw_polygon(ctx, polygon)
        ctx.fill()
else:
    polygon = Polygon(coordinates)
    CairoHelper.draw_polygon(ctx, polygon)
    ctx.fill()

lines2 = LineString([[10,10],[10,90],[90,90],[90,10]])
ctx.set_source_rgba(random(), random(), random(), 1)
CairoHelper.draw_line_string(ctx, apply_noise(complexify_linestring(lines2, 10), 12))
ctx.stroke()

polygon = Polygon([[10,10],[10,90],[90,90],[90,10]])
polygon = affinity.translate(polygon, 100, 100)
complex_polygon = complexify_polygon(polygon, 5)
ctx.set_source_rgba(random(), random(), random(), 1)
CairoHelper.draw_polygon(ctx, complex_polygon)
ctx.fill()

ctx.set_source_rgba(random(), random(), random(), 1)
for exterior_coord in complex_polygon.exterior.coords:
    CairoHelper.draw_point(ctx, Point(exterior_coord), 2)
    ctx.fill()

complex_polygon = affinity.translate(complex_polygon, 0, 100)
noisy_polygons = polygon_noise(complex_polygon, 18)
for noisy_polygon in noisy_polygons:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, noisy_polygon)
    ctx.fill()
    ctx.set_source_rgba(random(), random(), random(), 1)
    for exterior_coord in noisy_polygon.exterior.coords:
        # CairoHelper.draw_point(ctx, Point(exterior_coord), 1)
        ctx.fill()

bowtie_polygon = Polygon([[10,10],[90,90],[90,10],[10,90]])
bowtie_polygon = affinity.translate(bowtie_polygon, 200, 0)
bowtie_multi_polygons = make_polygon_simple(bowtie_polygon)
for bowtie_multi_polygon_geoms in bowtie_multi_polygons.geoms:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, bowtie_multi_polygon_geoms)
    ctx.fill()

bowtie_polygon = affinity.translate(bowtie_polygon, 0, 100)
bowtie_polygon = complexify_polygon(bowtie_polygon, 5)
bowtie_multi_polygons = make_polygon_simple(bowtie_polygon)
for bowtie_multi_polygon_geom in bowtie_multi_polygons.geoms:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, bowtie_multi_polygon_geom)
    ctx.fill()
    ctx.set_source_rgba(random(), random(), random(), 1)
    for exterior_coord in bowtie_multi_polygon_geom.exterior.coords:
        CairoHelper.draw_point(ctx, Point(exterior_coord), 2)
        ctx.fill()

bowtie_polygon = affinity.translate(bowtie_polygon, 0, 100)
noisy_bowtie_polygons = polygon_noise(bowtie_polygon, 18)
for noisy_bowtie_polygon in noisy_bowtie_polygons:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, noisy_bowtie_polygon)
    ctx.fill()




interior_polygon = Polygon([[10,10],[90,10],[90,90],[10,90]], [[[30,5],[30,80],[45,80],[45,20]], [[55,20],[55,80],[70,80],[70,20]]])
interior_polygon = affinity.translate(interior_polygon, 300, 0)
interior_polygon_multi_polygons = make_polygon_simple(interior_polygon)
for interior_polygon_multi_polygons_geom in interior_polygon_multi_polygons.geoms:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, interior_polygon_multi_polygons_geom)
    ctx.fill()

interior_polygon = affinity.translate(interior_polygon, 0, 100)
interior_polygon = complexify_polygon(interior_polygon, 5)
interior_multi_polygons = make_polygon_simple(interior_polygon)
for interior_multi_polygons_geom in interior_multi_polygons.geoms:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, interior_multi_polygons_geom)
    ctx.fill()

    ctx.set_source_rgba(random(), random(), random(), 1)
    for exterior_coord in interior_multi_polygons_geom.exterior.coords:
        CairoHelper.draw_point(ctx, Point(exterior_coord), 2)
        ctx.fill()

    for interiors in interior_multi_polygons_geom.interiors:
        ctx.set_source_rgba(random(), random(), random(), 1)
        for interior_coord in interiors.coords:
            CairoHelper.draw_point(ctx, Point(interior_coord), 2)
            ctx.fill()

interior_polygon = affinity.translate(interior_polygon, 0, 100)
noisy_interior_polygons = polygon_noise(interior_polygon, 18)
for noisy_interior_polygon in noisy_interior_polygons:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, noisy_interior_polygon)
    ctx.fill()


surface.flush()
surface.finish()
