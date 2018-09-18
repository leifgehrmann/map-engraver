import math
import cairocffi as cairo
import map.features.buildings
from shapely.geometry import Polygon

surface = cairo.PDFSurface("output/map_features_buildings_basic.pdf", 420, 110)
ctx = cairo.Context(surface)

w = 2
for i in range(0, 200):
    polygons = [Polygon([[10 + i * w, 10], [10 + (i + 1) * w, 10], [10 + (i + 1) * w, 100], [10 + i * w, 100]])]
    basicBuildingDrawer = map.features.buildings.Basic()
    basicBuildingDrawer.set_line_angle(math.fmod(i / 25 * math.pi / 2, math.pi))
    basicBuildingDrawer.set_line_separation(0.4)
    basicBuildingDrawer.draw(ctx, polygons)

surface.flush()
surface.finish()
