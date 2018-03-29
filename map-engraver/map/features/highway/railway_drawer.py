from graphicshelper import CairoHelper
from shapely.geometry import LineString
from cairocffi import Context
from typing import List, Union, Callable, no_type_check
from ..utilities import ProgressController


class RailwayDrawer(ProgressController):

    def __init__(self):
        pass

    def draw_railways(self, ctx: Context, railways: List[LineString]):
        # font = cairo.ToyFontFace('CMU Concrete', weight=1)
        # ctx.set_font_face(font)
        ctx.set_line_width(0.1)
        ctx.set_source_rgba(0, 0, 0, 1)
        self._draw_iterator(ctx, railways, self._draw_railway)

    def _draw_iterator(
            self,
            ctx: Context,
            line_strings: List[Union[LineString]],
            render_function: Callable[[Context, Union[LineString]], no_type_check]
    ):
        total = len(line_strings)
        for line_string in line_strings:
            render_function(ctx, line_string)
            if self.progress_callable is not None:
                self.progress_callable(render_function.__name__, 1, total)

    def _draw_railway(self, ctx: Context, line_string: Union[LineString]):
        CairoHelper.draw_line_string(ctx, line_string)

        # Todo: Buffer the linestring outwards
        # ShapelyHelper.buffer_linestring()

        ctx.stroke()
