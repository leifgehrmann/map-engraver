import math
import cairocffi as cairo
from shapely.geometry import Point, Polygon, LinearRing

from graphicshelper import CairoHelper, ShapelyHelper
from map.features.generic import ShadowInsetDrawer

surface = cairo.PDFSurface("output/map_features_generic_shadow_inset_drawer.pdf", 210, 210)
ctx = cairo.Context(surface)

for i in range(-16, 16):
    theta = i / 16 * math.pi
    radius = 30
    text_center = Point(150, 50)
    text_offset = Point(text_center.x + math.cos(theta) * radius, text_center.y + math.sin(theta) * radius)
    ctx.set_source_rgba(0, 0, 0, 0.5)
    ctx.set_font_size(1.5)
    ctx.move_to(text_offset.x, text_offset.y)
    ctx.show_text("%.2fπ" % (theta / math.pi))
    ctx.move_to(text_offset.x, text_offset.y + 2)
    ctx.show_text("%.2f" % (ShapelyHelper.get_direction(text_center, text_offset)))

for x in range(0, 21):
    for y in range(0, 21):

        min_angle = (x / 20 - 0.5) * 2 * math.pi * 2
        max_angle = (y / 20 - 0.5) * 2 * math.pi * 2

        circle = Point(x * 10 + 5, y * 10 + 5).buffer(4, resolution=5)  # type: Polygon

        if max_angle >= min_angle:
            ctx.set_source_rgba(1, 1, 0, 0.5)
        else:
            continue

        min_circle = Point(x * 10 + 5 + math.cos(min_angle + math.pi / 2) * 4, y * 10 + 5 + math.sin(min_angle + math.pi / 2) * 4).buffer(0.5, resolution=5)
        max_circle = Point(x * 10 + 5 + math.cos(max_angle + math.pi / 2) * 4, y * 10 + 5 + math.sin(max_angle + math.pi / 2) * 4).buffer(0.5, resolution=5)

        CairoHelper.draw_polygon(ctx, circle)
        ctx.fill_preserve()

        ctx.set_line_width(0.5)
        ctx.set_source_rgba(1, 0, 0, 0.25)
        ctx.stroke()

        CairoHelper.draw_polygon(ctx, min_circle)
        ctx.set_source_rgba(0, 1, 0, 0.5)
        ctx.fill()
        CairoHelper.draw_polygon(ctx, max_circle)
        ctx.set_source_rgba(1, 0, 0, 0.5)
        ctx.fill()

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
