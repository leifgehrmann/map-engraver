import math
from random import random
from shapely.ops import unary_union
from shapely.ops import polygonize

import cairocffi as cairo

from graphicshelper.cairo_helper import CairoHelper

from shapely.geometry import Polygon
from shapely.geometry import LineString

surface = cairo.PDFSurface("output/noisy_polygon.pdf", 400, 400)
ctx = cairo.Context(surface)

coordinates = []

for i in range(0, 20 * 10):
    coordinates.append([math.sin(i / 10 * math.pi / 10 * 3) * 200 + 200, math.cos(i / 10 * math.pi / 10) * 200 + 200])

# original data
line_string = LineString(coordinates)
# closed, non-simple
linear_ring = LineString(line_string.coords[:] + line_string.coords[0:1])

# Apply noise to line string here
# Todo:

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

surface.flush()
surface.finish()
