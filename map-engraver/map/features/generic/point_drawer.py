from cairocffi import Context
from shapely.geometry import Point
from typing import Union, List, Callable, no_type_check

from graphicshelper import CairoHelper
from map.features.utilities import ProgressController


class PointDrawer(ProgressController):
    size = 1
    circle_fill_set = False
    circle_fill_color = (0, 0, 0, 1)
    circle_stroke_set = False
    circle_stroke_color = (0, 0, 0, 1)
    circle_stroke_width = 1

    def set_size(self, size: float) -> 'PointDrawer':
        self.size = size
        return self

    def set_circle_fill_color(
            self,
            red: float,
            green: float,
            blue: float,
            alpha: float = 1
    ) -> 'PointDrawer':
        self.circle_fill_set = True
        self.circle_fill_color = (red, green, blue, alpha)
        return self

    def set_circle_stroke_color(
            self,
            red: float,
            green: float,
            blue: float,
            alpha: float = 1
    ) -> 'PointDrawer':
        self.circle_stroke_set = True
        self.circle_stroke_color = (red, green, blue, alpha)
        return self

    def set_circle_stroke_width(self, width) -> 'PointDrawer':
        self.circle_stroke_set = True
        self.circle_stroke_width = width
        return self

    def draw(self, ctx: Context, points: List[Point]):

        if self.circle_stroke_set:
            ctx.set_source_rgba(*self.circle_stroke_color)
            ctx.set_line_width(self.circle_stroke_width)
            self._draw_iterator(ctx, points, self._draw_stroke)

        if self.circle_fill_set:
            ctx.set_source_rgba(*self.circle_fill_color)
            self._draw_iterator(ctx, points, self._draw_fill)

    def _draw_iterator(
            self,
            ctx: Context,
            points: List[Point],
            render_function: Callable[
                [Context, Union[Point]],
                no_type_check
            ]
    ):
        total = len(points)
        for point in points:
            render_function(ctx, point)
            if self.progress_callable is not None:
                self.progress_callable(render_function.__name__, 1, total)

    def _draw_fill(self, ctx: Context, geom: Point):
        CairoHelper.draw_circle(ctx, geom, self.size)
        ctx.fill()

    def _draw_stroke(self, ctx: Context, geom: Point):
        CairoHelper.draw_circle(ctx, geom, self.size)
        ctx.stroke()
