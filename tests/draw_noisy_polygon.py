import math
from random import random
from shapely.ops import unary_union
from shapely.ops import polygonize
from shapely import affinity

import cairocffi as cairo

from graphicshelper.cairo_helper import CairoHelper

from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString

surface = cairo.PDFSurface("output/noisy_polygon.pdf", 400, 400)
ctx = cairo.Context(surface)


def complexify_linestring(linestring: LineString, tolerance: float):
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


def complexify_polygon(polygon: Polygon, tolerance: float):
    exterior_linestring = LineString(polygon.exterior.coords)
    complex_exterior = complexify_linestring(exterior_linestring, tolerance)
    complex_interior = []
    for interior in polygon.interiors:
        complex_interior.append(complexify_linestring(LineString(interior.coords), tolerance))
    return Polygon(complex_exterior, complex_interior)


# Apply noise to line string here
def apply_noise(linestring: LineString):
    new_linestring_coords = []
    for x, y in linestring.coords:
        new_linestring_coords.append((random() * 12 - 6 + x, random() * 12 - 6 + y))
    return LineString(new_linestring_coords)

coordinates = []

for i in range(0, 20 * 10):
    coordinates.append([math.sin(i / 10 * math.pi / 10 * 3) * 200 + 200, math.cos(i / 10 * math.pi / 10) * 200 + 200])

# original data
line_string = LineString(coordinates)

line_string = apply_noise(line_string)
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
CairoHelper.draw_line_string(ctx, apply_noise(complexify_linestring(lines2, 10)))
ctx.stroke()

polygon = Polygon([[10,10],[10,90],[90,90],[90,10]])
polygon = affinity.translate(polygon, 100, 0)
complex_polygon = complexify_polygon(polygon, 10)
CairoHelper.draw_polygon(ctx, complex_polygon)
ctx.stroke()

for exterior_coord in complex_polygon.exterior.coords:
    CairoHelper.draw_point(ctx, Point(exterior_coord), 5)
    ctx.fill()

surface.flush()
surface.finish()
