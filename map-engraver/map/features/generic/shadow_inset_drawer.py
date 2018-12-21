from typing import List, Union

from cairocffi import Context
from shapely.geometry import Polygon, MultiPolygon, LineString
import math

from graphicshelper import ShapelyHelper, CairoHelper


class ShadowInsetDrawer:
    outline_line_width = 0.05
    shadow_line_width = 0.2
    min_angle = -math.pi / 6 * 4
    max_angle = math.pi / 6

    def draw(self, ctx: Context, outline: Union[Polygon, MultiPolygon]):
        if isinstance(outline, MultiPolygon):
            shadow_line_strings = []
            for sub_outline in outline.geoms:
                shadow_line_string = self.draw(ctx, sub_outline)
                shadow_line_strings.append(shadow_line_string)
            return shadow_line_strings
        buffered_outline = outline.buffer(-self.outline_line_width / 2, cap_style=3, join_style=2)

        shadow_line_strings = self._get_shadow_lines(buffered_outline)
        for shadow_line_string in shadow_line_strings:
            CairoHelper.draw_line_string(ctx, shadow_line_string)
            ctx.stroke()
        pass

    def _get_shadow_lines(self, geometry: Union[Polygon, MultiPolygon]) -> List[LineString]:
        multi_line_string = []
        offset_amount = -(self.outline_line_width - self.shadow_line_width / 2)

        if isinstance(geometry, Polygon):
            multi_line_string = ShapelyHelper.get_directional_line_strings_from_polygon(
                geometry,
                self.min_angle,
                self.max_angle
            )
        elif isinstance(geometry, MultiPolygon):
            multi_line_string = ShapelyHelper.get_directional_line_strings_from_multipolygon(
                geometry,
                self.min_angle,
                self.max_angle
            )

        buffered_line_strings = []
        for line_string in multi_line_string.geoms:
            if not isinstance(line_string, LineString):
                print(line_string)
                continue
            try:
                buffered_line_string = line_string.parallel_offset(offset_amount, join_style=2, mitre_limit=5)
            except ValueError:
                continue
            if isinstance(buffered_line_string, LineString):
                buffered_line_strings.append(buffered_line_string)

        return buffered_line_strings
