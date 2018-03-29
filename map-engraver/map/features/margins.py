from cairocffi import Context
from shapely.geometry import Polygon
from graphicshelper import CairoHelper


class Margins:
    def __init__(self):
        self.margin_set = False
        self.margin_left = None
        self.margin_right = None
        self.margin_top = None
        self.margin_bottom = None
        self.legend_set = False
        self.legend_left = None
        self.legend_right = None
        self.legend_top = None
        self.legend_bottom = None
        self.canvas_set = False
        self.canvas_width = None
        self.canvas_height = None

    def set_canvas_size(self, width: float, height: float) -> 'Margins':
        self.canvas_width = width
        self.canvas_height = height
        self.canvas_set = True
        return self

    def set_margin(self, top: float, right: float, bottom: float, left: float) -> 'Margins':
        self.margin_top = top
        self.margin_right = right
        self.margin_bottom = bottom
        self.margin_left = left
        self.margin_set = True
        return self

    def set_legend(self, top: float, right: float, bottom: float, left: float) -> 'Margins':
        self.legend_top = top
        self.legend_right = right
        self.legend_bottom = bottom
        self.legend_left = left
        self.legend_set = True
        return self

    def draw(self, ctx: Context):

        if not self.canvas_set or not self.margin_set or not self.legend_set:
            raise Exception("Canvas, margin or legend not set!")

        margin_exterior_top_left = (0, 0)
        margin_exterior_top_right = (self.canvas_width, 0)
        margin_exterior_bottom_left = (0, self.canvas_height)
        margin_exterior_bottom_right = (self.canvas_width, self.canvas_height)
        legend_exterior_top_left = (self.margin_left, self.margin_top)
        legend_exterior_top_right = (self.canvas_width - self.margin_right, self.margin_top)
        legend_exterior_bottom_left = (self.margin_left, self.canvas_height - self.margin_bottom)
        legend_exterior_bottom_right = (self.canvas_width - self.margin_right, self.canvas_height - self.margin_bottom)
        legend_interior_top_left = (self.margin_left + self.legend_left, self.margin_top + self.legend_top)
        legend_interior_top_right = (self.canvas_width - self.margin_right - self.legend_right, self.margin_top + self.legend_top)
        legend_interior_bottom_left = (self.margin_left + self.legend_left, self.canvas_height - self.margin_bottom - self.legend_bottom)
        legend_interior_bottom_right = (
            self.canvas_width - self.margin_right - self.legend_right,
            self.canvas_height - self.margin_bottom - self.legend_bottom
        )

        margin_and_legend = Polygon(
            [
                margin_exterior_top_left,
                margin_exterior_top_right,
                margin_exterior_bottom_right,
                margin_exterior_bottom_left,
                margin_exterior_top_left
            ],
            [
                list(reversed([
                    legend_interior_top_left,
                    legend_interior_top_right,
                    legend_interior_bottom_right,
                    legend_interior_bottom_left,
                    legend_interior_top_left
                ]))
            ]
        )

        legend_exterior = Polygon(
            [
                legend_exterior_top_left,
                legend_exterior_top_right,
                legend_exterior_bottom_right,
                legend_exterior_bottom_left,
                legend_exterior_top_left
            ]
        )

        legend_interior = Polygon(
            [
                legend_exterior_top_left,
                legend_exterior_top_right,
                legend_exterior_bottom_right,
                legend_exterior_bottom_left,
                legend_exterior_top_left
            ],
            [
                list(reversed([
                    legend_interior_top_left,
                    legend_interior_top_right,
                    legend_interior_bottom_right,
                    legend_interior_bottom_left,
                    legend_interior_top_left
                ]))
            ]
        )

        ctx.set_line_width(0.05)

        ctx.set_source_rgb(1, 1, 1)
        CairoHelper.draw_polygon(ctx, margin_and_legend)
        ctx.fill()

        ctx.set_source_rgb(0, 0, 0)
        CairoHelper.draw_polygon(ctx, legend_exterior)
        ctx.stroke()
        CairoHelper.draw_polygon(ctx, legend_interior)
        ctx.stroke()
