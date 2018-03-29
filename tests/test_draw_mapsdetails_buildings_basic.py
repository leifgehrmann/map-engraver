import math

import cairocffi as cairo

surface = cairo.PDFSurface("../data/output/test_draw_mapdetails_buildings_basic.pdf", 400, 400)
ctx = cairo.Context(surface)

from shapely.geometry import Polygon

w = 2
for i in range(0, 200):
    print("------------------")
    polygons = []
    polygons.append(Polygon([[4 + i*w,10], [4 + (i+1)*w,10], [4+ (i+1)*w,100], [4+ i*w,100]]))
    basicBuildingDrawer = map.features.buildings.Basic(math.fmod(i / 25 * math.pi / 2, math.pi), 0.4)
    basicBuildingDrawer.draw(ctx, polygons)

surface.flush()
surface.finish()