import math
import cairocffi as cairo
import map.features.buildings
from shapely.geometry import Point

from graphicshelper import CairoHelper
from map.features.generic import ShadowInsetDrawer

surface = cairo.PDFSurface("output/map_features_generic_shadow_inset_drawer.pdf", 210, 210)
ctx = cairo.Context(surface)

for x in range(0, 21):
    for y in range(0, 21):

        min_angle = (x / 20 - 0.5) * 2 * math.pi * 2
        max_angle = (y / 20 - 0.5) * 2 * math.pi * 2

        circle = Point(x * 10 + 5, y * 10 + 5).buffer(4, resolution=5)
        if max_angle >= min_angle:
            ctx.set_source_rgba(1, 0, 0, 0.5)
        else:
            ctx.set_source_rgba(1, 0, 0, 0.25)
        CairoHelper.draw_polygon(ctx, circle)
        ctx.fill_preserve()

        ctx.set_line_width(0.5)
        ctx.set_source_rgba(0, 1, 0, 0.25)
        ctx.stroke()

        ctx.set_line_width(1)
        ctx.set_source_rgba(0, 0, 1, 0.5)
        shadow_inset_drawer = ShadowInsetDrawer()
        shadow_inset_drawer.min_angle = min_angle
        shadow_inset_drawer.max_angle = max_angle
        shadow_inset_drawer.outline_line_width = 0.5
        shadow_inset_drawer.shadow_line_width = 1
        shadow_inset_drawer.draw(ctx, circle)

        ctx.set_source_rgba(0, 0, 0, 0.5)
        ctx.set_font_size(1.5)
        ctx.move_to(x * 10 + 3, y * 10 + 4.5)
        ctx.show_text("%.2fπ" % (shadow_inset_drawer.min_angle/math.pi))
        ctx.move_to(x * 10 + 3, y * 10 + 6.5)
        ctx.show_text("%.2fπ" % (shadow_inset_drawer.max_angle / math.pi))

surface.flush()
surface.finish()
