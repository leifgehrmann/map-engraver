from cairocffi import Context
from shapely.geometry import Polygon, MultiPolygon
from typing import Union, List, Callable, no_type_check

from graphicshelper import CairoHelper
from map.features.utilities import ProgressController


class PolygonDrawer(ProgressController):

    fill_set = False
    fill_color = (0, 0, 0, 1)
    stroke_set = False
    stroke_color = (0, 0, 0, 1)
    stroke_width = 1

    def set_fill_color(self, red, green, blue, alpha=1) -> 'PolygonDrawer':
        self.fill_set = True
        self.fill_color = (red, green, blue, alpha)
        return self

    def set_stroke_color(self, red, green, blue, alpha=1) -> 'PolygonDrawer':
        self.stroke_set = True
        self.stroke_color = (red, green, blue, alpha)
        return self

    def set_stroke_width(self, width) -> 'PolygonDrawer':
        self.stroke_set = True
        self.stroke_width = width
        return self

    def draw(self, ctx: Context, polygons: List[Union[Polygon, MultiPolygon]]):
        if self.stroke_set:
            ctx.set_source_rgba(*self.stroke_color)
            ctx.set_line_width(self.stroke_width)
            self._draw_iterator(ctx, polygons, self._draw_stroke)

        if self.fill_set:
            ctx.set_source_rgba(*self.fill_color)
            self._draw_iterator(ctx, polygons, self._draw_fill)

    def _draw_iterator(
            self,
            ctx: Context,
            polygons: List[Union[Polygon, MultiPolygon]],
            render_function: Callable[
                [Context, Union[Polygon, MultiPolygon]],
                no_type_check
            ]
    ):
        total = len(polygons)
        for polygon in polygons:
            render_function(ctx, polygon)
            if self.progress_callable is not None:
                self.progress_callable(render_function.__name__, 1, total)

    def _draw_fill(self, ctx: Context, geom: Union[Polygon, MultiPolygon]):
        if isinstance(geom, MultiPolygon):
            for sub_geom in geom.geoms:
                self._draw_fill(ctx, sub_geom)
            return
        CairoHelper.draw_polygon(ctx, geom)
        ctx.fill()

    def _draw_stroke(self, ctx: Context, geom: Union[Polygon, MultiPolygon]):
        if isinstance(geom, MultiPolygon):
            for sub_geom in geom.geoms:
                self._draw_stroke(ctx, sub_geom)
            return
        CairoHelper.draw_polygon(ctx, geom)
        ctx.stroke()
