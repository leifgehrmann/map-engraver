from graphicshelper import CairoHelper
from shapely.geometry import Polygon, MultiPolygon
from cairocffi import Context
from typing import List, Union, Callable, no_type_check
from ..utilities import ProgressController
import math


class WaterDrawer(ProgressController):

    water_shadow = 0.08
    line_width = 0.05
    high_quality = True

    def draw(self, ctx: Context, polygons: List[Union[Polygon, MultiPolygon]]):
        if self.high_quality:
            ctx.set_source_rgb(0, 0, 0)
            ctx.set_line_width(self.line_width)
            self._draw_iterator(ctx, polygons, self._draw_water)
        else:
            ctx.set_source_rgba(0, 0, 0, 0.3)
            self._draw_iterator(ctx, polygons, self._draw_water_area)

    def _draw_iterator(
            self,
            ctx: Context,
            polygons: List[Union[Polygon, MultiPolygon]],
            render_function: Callable[[Context, Union[Polygon, MultiPolygon]], no_type_check]
    ):
        total = len(polygons)
        for polygon in polygons:
            render_function(ctx, polygon)
            if self.progress_callable is not None:
                self.progress_callable(render_function.__name__, 1, total)

    def _draw_water_area(self, ctx: Context, outline: Union[Polygon, MultiPolygon]):
        CairoHelper.draw_polygon(ctx, outline)
        ctx.fill()

    def _draw_water(self, ctx: Context, outline: Union[Polygon, MultiPolygon]):
        # Draw outline of ripple
        CairoHelper.draw_polygon(ctx, outline)
        ctx.stroke()

        self._draw_ripples(ctx, outline)

    def _draw_ripples(self, ctx: Context, ripple: Union[Polygon, MultiPolygon], iteration: int=0):

        if iteration > 100:
            print("BAD BAD SHAPELY")
            return

        if isinstance(ripple, Polygon):
            # Draw current iteration of ripple
            if iteration > 0:
                self._draw_ripple(ctx, ripple, iteration)

            # If ripple has no coordinates, don't bother rippling any further
            if not hasattr(ripple.exterior, 'coords'):
                return

            # Draw next iteration of ripple
            ripple_buffered = self._buffer_ripple(ripple, iteration + 1)
            self._draw_ripples(ctx, ripple_buffered, iteration + 1)
        elif isinstance(ripple, MultiPolygon):
            for geom in ripple.geoms:
                self._draw_ripples(ctx, geom, iteration)

    def _draw_ripple(self, ctx: Context, ripple: Polygon, iteration: int):
        CairoHelper.draw_polygon(ctx, ripple)
        ctx.stroke()

    def _buffer_ripple(self, ripple: Polygon, iteration: int):
        # Fuzzy up the original ripple
        new_lines = []
        interpolation_distance = ripple.length
        # ripple.interpolate()


        # Buffer from the now fuzzy ripple
        buffer_distance = self._iteration_distance(iteration)
        ripple_buffered = ripple.buffer(-buffer_distance).simplify(self.line_width)

        return ripple_buffered

    def _iteration_distance(self, iteration) -> float:
        return self.line_width * ((math.atan((iteration - 4) / 2) / math.pi + 1 / 2) * 4 + 2) * 3 / 2
