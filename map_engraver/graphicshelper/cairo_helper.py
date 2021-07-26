from shapely.geometry import Polygon, LineString, Point
from cairocffi import Context


class CairoHelper:
    @staticmethod
    def draw_point(ctx: Context, point: Point, size):
        ctx.arc(point.x, point.y, size / 2, 0, 2 * 3.1416)
        ctx.fill()

    @staticmethod
    def draw_circle(ctx: Context, point: Point, size):
        ctx.arc(point.x, point.y, size / 2, 0, 2 * 3.1416)

    @staticmethod
    def draw_line_string(ctx: Context, line_string: LineString):
        start = True
        for x, y in line_string.coords:
            if start:
                ctx.move_to(x, y)
            else:
                ctx.line_to(x, y)

            start = False

    @staticmethod
    def draw_polygon(ctx: Context, polygon: Polygon):
        if hasattr(polygon.exterior, 'coords'):
            start = True
            ctx.new_path()
            for x, y in polygon.exterior.coords:
                if start:
                    ctx.move_to(x, y)
                else:
                    ctx.line_to(x, y)

                start = False

        for interior in polygon.interiors:
            ctx.new_sub_path()
            start = True
            for x, y in interior.coords:
                if start:
                    ctx.move_to(x, y)
                else:
                    ctx.line_to(x, y)

                start = False
            ctx.close_path()

        ctx.close_path()
