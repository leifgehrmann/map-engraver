from cairocffi import Context
from shapely.geometry import LineString, MultiLineString
from typing import Union, List, Callable, no_type_check

from graphicshelper import CairoHelper
from map.features.utilities import ProgressController


class LineStringDrawer(ProgressController):

    stroke_color = (0, 0, 0, 1)
    stroke_width = 1

    def set_stroke_color(self, red, green, blue, alpha=1) -> 'LineStringDrawer':
        self.stroke_color = (red, green, blue, alpha)
        return self

    def set_stroke_width(self, width) -> 'LineStringDrawer':
        self.stroke_width = width
        return self

    def draw(self, ctx: Context, line_strings: List[Union[LineString, MultiLineString]]):
        ctx.set_source_rgba(*self.stroke_color)
        ctx.set_line_width(self.stroke_width)
        self._draw_iterator(ctx, line_strings, self._draw_stroke)

    def _draw_iterator(
            self,
            ctx: Context,
            line_strings: List[Union[LineString, MultiLineString]],
            render_function: Callable[
                [Context, Union[LineString, MultiLineString]],
                no_type_check
            ]
    ):
        total = len(line_strings)
        for lineString in line_strings:
            render_function(ctx, lineString)
            if self.progress_callable is not None:
                self.progress_callable(render_function.__name__, 1, total)

    def _draw_stroke(self, ctx: Context, geom: Union[LineString, MultiLineString]):
        if isinstance(geom, MultiLineString):
            for sub_geom in geom.geoms:
                self._draw_stroke(ctx, sub_geom)
            return
        CairoHelper.draw_line_string(ctx, geom)
        ctx.stroke()
