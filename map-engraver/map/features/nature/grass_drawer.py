from graphicshelper import CairoHelper
from shapely.geometry import Polygon, MultiPolygon
from cairocffi import Context
from typing import List, Union, Callable, no_type_check
from ..utilities import ProgressController


class GrassDrawer(ProgressController):

    def draw(self, ctx: Context, grasses: List[Union[Polygon, MultiPolygon]]):
        self._draw_grasses_iterator(ctx, grasses, self._draw_grass_area)

    def _draw_grasses_iterator(
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

    def _draw_grass_area(self, ctx: Context, outline: Union[Polygon, MultiPolygon]):
        if hasattr(outline, 'osm_tags'):
            tags = outline.osm_tags
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
