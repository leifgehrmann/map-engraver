import cairocffi as cairo
from shapely.geometry import Point
import map.features.nature

circle = Point(50, 50).buffer(40, resolution=30)
bite = Point(20, 50).buffer(20)
hole = Point(60, 50).buffer(10)
circle = circle.difference(bite)
circle = circle.difference(hole)

print(circle)

surface = cairo.PDFSurface("output/map_features_nature_water.pdf", 100, 100)
ctx = cairo.Context(surface)

waterDrawer = map.features.nature.WaterDrawer()
waterDrawer.draw(ctx, [circle])

surface.flush()
surface.finish()
