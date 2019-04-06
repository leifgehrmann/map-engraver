from graphicshelper import CairoHelper
from cairocffi import Context
from typing import List, Callable, no_type_check

from osmshapely import Polygon
from ..utilities import ProgressController


class GrassDrawer(ProgressController):

    def draw(self, ctx: Context, grasses: List[Polygon]):
        self._draw_grasses_iterator(ctx, grasses, self._draw_grass_area)

    def _draw_grasses_iterator(
            self,
            ctx: Context,
            polygons: List[Polygon],
            render_function: Callable[[Context, Polygon], no_type_check]
    ):
        total = len(polygons)
        for polygon in polygons:
            render_function(ctx, polygon)
            if self.progress_callable is not None:
                self.progress_callable(render_function.__name__, 1, total)

    def _draw_grass_area(self, ctx: Context, outline: Polygon):
            tags = outline.get_osm_tags()
            if 'leisure' in tags and tags['leisure'] == 'park':
                ctx.set_source_rgba(0, 0, 0, 0.03)
            elif 'leisure' in tags and tags['leisure'] == 'garden':
                ctx.set_source_rgba(0, 0, 0, 0.1)
            elif 'leisure' in tags and tags['leisure'] == 'common':
                ctx.set_source_rgba(0, 0, 0, 0.03)
            elif 'leisure' in tags and tags['leisure'] == 'recreation_ground':
                ctx.set_source_rgba(0, 0, 0, 0.03)
            elif 'landuse' in tags and tags['landuse'] == 'grass':
                ctx.set_source_rgba(0, 0, 0, 0.03)
            elif 'landuse' in tags and tags['landuse'] == 'forest':
                ctx.set_source_rgba(0, 0, 0, 0.03)
            elif 'natural' in tags and tags['natural'] == 'wood':
                ctx.set_source_rgba(0, 0, 0, 0.03)
            CairoHelper.draw_polygon(ctx, outline)
            ctx.fill()
