from cairocffi import Context
from shapely.geometry import Polygon
from graphicshelper import CairoHelper


class Background:
    def __init__(self):
        self.canvas_width = None
        self.canvas_height = None
        self.canvas_set = False
        self.color = (1, 1, 1, 1)

    def set_canvas_size(self, width: float, height: float) -> 'Background':
        self.canvas_width = width
        self.canvas_height = height
        self.canvas_set = True
        return self

    def set_color(
            self,
            red: float,
            green: float,
            blue: float,
            alpha: float = 1
    ) -> 'Background':
        self.color = (red, green, blue, alpha)
        return self

    def draw(self, ctx: Context):

        if not self.canvas_set:
            raise Exception("Canvas size not set!")

        top_left = (0, 0)
        top_right = (self.canvas_width, 0)
        bottom_left = (0, self.canvas_height)
        bottom_right = (self.canvas_width, self.canvas_height)

        canvas = Polygon([
            top_left,
            top_right,
            bottom_right,
            bottom_left,
            top_left
        ])

        ctx.set_source_rgba(*self.color)
        CairoHelper.draw_polygon(ctx, canvas)
        ctx.fill()
