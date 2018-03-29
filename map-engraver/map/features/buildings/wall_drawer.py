from graphicshelper import CairoHelper
from shapely.geometry import LineString
from cairocffi import Context
from typing import List, Union, Callable, no_type_check
from ..utilities import ProgressController


class WallDrawer(ProgressController):

    def draw_walls(self, ctx: Context, walls: List[LineString]):
        ctx.set_line_width(0.05)
        ctx.set_source_rgba(0, 0, 0, 1)
        self._draw_iterator(ctx, walls, self._draw_wall)

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

    def _draw_wall(self, ctx: Context, line_string: Union[LineString]):
        CairoHelper.draw_line_string(ctx, line_string)
        ctx.stroke()
