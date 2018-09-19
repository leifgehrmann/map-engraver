import math
from random import random
from shapely.ops import unary_union
from shapely.ops import polygonize
from shapely import affinity

import cairocffi as cairo

from graphicshelper.cairo_helper import CairoHelper
from graphicshelper.shapely_helper import ShapelyHelper

from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString

surface = cairo.PDFSurface("output/graphicshelper_shapely_helper_polygon_noise.pdf", 400, 400)
ctx = cairo.Context(surface)

coordinates = []

for i in range(0, 20 * 10):
    coordinates.append([math.sin(i / 10 * math.pi / 10 * 3) * 200 + 200, math.cos(i / 10 * math.pi / 10) * 200 + 200])

# original data
line_string = LineString(coordinates)

line_string = ShapelyHelper.linestring_noise_random_square(line_string, 12)
# closed, non-simple
linear_ring = LineString(line_string.coords[:] + line_string.coords[0:1])

if not linear_ring.is_simple:
    multi_line_string = unary_union(linear_ring)
    for polygon in polygonize(multi_line_string):
        ctx.set_source_rgba(random(), random(), random(), 1)
        CairoHelper.draw_polygon(ctx, polygon)
        ctx.fill()
else:
    polygon = Polygon(coordinates)
    CairoHelper.draw_polygon(ctx, polygon)
    ctx.fill()

lines2 = LineString([[10, 10], [10, 90], [90, 90], [90, 10]])
ctx.set_source_rgba(random(), random(), random(), 1)
CairoHelper.draw_line_string(ctx, ShapelyHelper.linestring_noise_random_square(
    ShapelyHelper.interpolate_line_string(lines2, 10), 12))
ctx.stroke()

polygon = Polygon([[10, 10], [10, 90], [90, 90], [90, 10]])
polygon = affinity.translate(polygon, 100, 100)
complex_polygon = ShapelyHelper.interpolate_polygon(polygon, 5)
ctx.set_source_rgba(random(), random(), random(), 1)
CairoHelper.draw_polygon(ctx, complex_polygon)
ctx.fill()

ctx.set_source_rgba(random(), random(), random(), 1)
for exterior_coord in complex_polygon.exterior.coords:
    CairoHelper.draw_point(ctx, Point(exterior_coord), 2)
    ctx.fill()

complex_polygon = affinity.translate(complex_polygon, 0, 100)
noisy_polygons = ShapelyHelper.polygon_noise(complex_polygon, ShapelyHelper.linestring_noise_random_square, 18)
for noisy_polygon in noisy_polygons:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, noisy_polygon)
    ctx.fill()
    ctx.set_source_rgba(random(), random(), random(), 1)
    for exterior_coord in noisy_polygon.exterior.coords:
        # CairoHelper.draw_point(ctx, Point(exterior_coord), 1)
        ctx.fill()

bowtie_polygon = Polygon([[10, 10], [90, 90], [90, 10], [10, 90]])
bowtie_polygon = affinity.translate(bowtie_polygon, 200, 0)
bowtie_multi_polygons = ShapelyHelper.convert_non_simple_polygon_to_multi_polygon(bowtie_polygon)
for bowtie_multi_polygon_geoms in bowtie_multi_polygons.geoms:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, bowtie_multi_polygon_geoms)
    ctx.fill()

bowtie_polygon = affinity.translate(bowtie_polygon, 0, 100)
bowtie_polygon = ShapelyHelper.interpolate_polygon(bowtie_polygon, 5)
bowtie_multi_polygons = ShapelyHelper.convert_non_simple_polygon_to_multi_polygon(bowtie_polygon)
for bowtie_multi_polygon_geom in bowtie_multi_polygons.geoms:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, bowtie_multi_polygon_geom)
    ctx.fill()
    ctx.set_source_rgba(random(), random(), random(), 1)
    for exterior_coord in bowtie_multi_polygon_geom.exterior.coords:
        CairoHelper.draw_point(ctx, Point(exterior_coord), 2)
        ctx.fill()

bowtie_polygon = affinity.translate(bowtie_polygon, 0, 100)
noisy_bowtie_polygons = ShapelyHelper.polygon_noise(bowtie_polygon, ShapelyHelper.linestring_noise_random_square, 2)
for noisy_bowtie_polygon in noisy_bowtie_polygons:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, noisy_bowtie_polygon)
    ctx.fill()

bowtie_polygon = affinity.translate(bowtie_polygon, 0, 100)
noisy_bowtie_polygons = ShapelyHelper.polygon_noise(bowtie_polygon, ShapelyHelper.linestring_noise_random_square, 18)
for noisy_bowtie_polygon in noisy_bowtie_polygons:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, noisy_bowtie_polygon)
    ctx.fill()

interior_polygon = Polygon([[10, 10], [90, 10], [90, 90], [10, 90]],
                           [[[30, 20], [30, 80], [45, 80], [45, 20]], [[55, 20], [55, 80], [70, 80], [70, 20]]])
interior_polygon = affinity.translate(interior_polygon, 300, 0)
interior_polygon_multi_polygons = ShapelyHelper.convert_non_simple_polygon_to_multi_polygon(interior_polygon)
for interior_polygon_multi_polygons_geom in interior_polygon_multi_polygons.geoms:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, interior_polygon_multi_polygons_geom)
    ctx.fill()

interior_polygon = affinity.translate(interior_polygon, 0, 100)
interior_polygon = ShapelyHelper.interpolate_polygon(interior_polygon, 5)
interior_multi_polygons = ShapelyHelper.convert_non_simple_polygon_to_multi_polygon(interior_polygon)
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
noisy_interior_polygons = ShapelyHelper.polygon_noise(
    interior_polygon,
    ShapelyHelper.linestring_noise_random_square,
    2
)
for noisy_interior_polygon in noisy_interior_polygons:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, noisy_interior_polygon)
    ctx.fill()

interior_polygon = affinity.translate(interior_polygon, 0, 100)
noisy_interior_polygons = ShapelyHelper.polygon_noise(
    interior_polygon,
    ShapelyHelper.linestring_noise_random_square,
    18
)
for noisy_interior_polygon in noisy_interior_polygons:
    ctx.set_source_rgba(random(), random(), random(), 1)
    CairoHelper.draw_polygon(ctx, noisy_interior_polygon)
    ctx.fill()

surface.flush()
surface.finish()
