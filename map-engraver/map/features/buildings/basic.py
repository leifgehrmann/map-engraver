from graphicshelper import CairoHelper
from shapely.geometry import Polygon, MultiPolygon, Point, LineString, MultiLineString
from cairocffi import Context
from typing import List, Union, Callable, no_type_check
import math

from map.features.generic import ShadowInsetDrawer
from ..utilities import ProgressController


class Basic(ProgressController):

    line_angle = 0
    line_separation = 1
    pattern_line_width = 0.05
    outline_line_width = 0.05
    shadow_line_width = 0.2
    high_quality = True

    def __init__(self):
        self.shadow_inset_drawer = ShadowInsetDrawer()
        self.shadow_inset_drawer.outline_line_width = self.outline_line_width
        self.shadow_inset_drawer.shadow_line_width = self.shadow_line_width

    def set_high_quality(self, high_quality: bool) -> 'Basic':
        self.high_quality = high_quality
        return self

    def set_line_angle(self, line_angle: float) -> 'Basic':
        self.line_angle = line_angle
        return self

    def set_line_separation(self, line_separation: float) -> 'Basic':
        self.line_separation = line_separation
        return self

    def draw(self, ctx: Context, buildings: List[Union[Polygon, MultiPolygon]]):
        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.set_line_width(self.outline_line_width)
        self._draw_building_iterator(ctx, buildings, self._draw_building_outline)
        if self.high_quality:
            ctx.set_line_width(self.pattern_line_width)
            self._draw_building_iterator(ctx, buildings, self._draw_building_pattern)
            ctx.set_line_width(self.shadow_line_width)
            self._draw_building_iterator(ctx, buildings, self._draw_building_shadow)
        else:
            ctx.set_source_rgba(0, 0, 0, 0.3)
            ctx.set_line_width(self.outline_line_width)
            self._draw_building_iterator(ctx, buildings, self._draw_building_interior)

    def _draw_building_iterator(
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

    def _draw_building_pattern(self, ctx: Context, outline: Union[Polygon, MultiPolygon]):

        # Get lines that would be within polygon boundaries to form pattern
        lines = Basic.get_lines_within_bounds(Point(0, 0), self.line_angle, self.line_separation, outline.bounds)

        # Intersect each line with the polygon forming small line segments
        for line in lines:
            intersected_lines = line.intersection(outline)
            if isinstance(intersected_lines, MultiLineString):
                for intersected_line in intersected_lines.geoms:
                    if isinstance(intersected_line, LineString):
                        CairoHelper.draw_line_string(ctx, intersected_line)
            elif isinstance(intersected_lines, LineString):
                CairoHelper.draw_line_string(ctx, intersected_lines)
        ctx.stroke()

    def _draw_building_outline(self, ctx: Context, outline: Union[Polygon, MultiPolygon]):
        if isinstance(outline, MultiPolygon):
            for sub_outline in outline.geoms:
                self._draw_building_outline(ctx, sub_outline)
            return
        CairoHelper.draw_polygon(ctx, outline)
        ctx.stroke()
        pass

    def _draw_building_interior(self, ctx: Context, outline: Union[Polygon, MultiPolygon]):
        if isinstance(outline, MultiPolygon):
            for sub_outline in outline.geoms:
                self._draw_building_outline(ctx, sub_outline)
            return
        CairoHelper.draw_polygon(ctx, outline)
        ctx.fill()
        pass

    def _draw_building_shadow(self, ctx: Context, outline: Union[Polygon, MultiPolygon]):
        self.shadow_inset_drawer.draw(ctx, outline)

    @staticmethod
    def get_lines_within_bounds(origin: Point, angle: float, separation: float, bounds) -> List[LineString]:
        top_left = Point(bounds[0], bounds[1])
        top_right = Point(bounds[2], bounds[1])
        bottom_left = Point(bounds[0], bounds[3])
        bottom_right = Point(bounds[2], bounds[3])

        separations = [
            Basic.get_offset_between_point_and_line(origin, angle, top_left),
            Basic.get_offset_between_point_and_line(origin, angle, top_right),
            Basic.get_offset_between_point_and_line(origin, angle, bottom_left),
            Basic.get_offset_between_point_and_line(origin, angle, bottom_right)
        ]

        min_separation = math.floor(min(separations) / separation) * separation
        max_separation = math.ceil(max(separations) / separation) * separation

        lines = []
        new_separation = min_separation
        while new_separation < max_separation:
            new_origin_x = origin.x - math.sin(angle) * new_separation
            new_origin_y = origin.y + math.cos(angle) * new_separation
            new_origin = Point(new_origin_x, new_origin_y)

            new_linestring = Basic.get_lines_within_box(new_origin, angle, bounds)
            if new_linestring is not None:
                lines.append(new_linestring)

            new_separation += separation

        return lines

    @staticmethod
    def get_offset_between_point_and_line(origin: Point, angle: float, point: Point):
        distance = Basic.get_shortest_distance_between_point_and_line(origin, angle, point)
        if Basic.is_point_above_line(origin, angle, point):
            return distance
        else:
            return -distance

    @staticmethod
    def get_shortest_distance_between_point_and_line(origin: Point, angle: float, point: Point):

        u_x = math.cos(angle)
        u_y = math.sin(angle)

        a_minus_p_x = origin.x - point.x
        a_minus_p_y = origin.y - point.y

        dot_product = u_x * a_minus_p_x + a_minus_p_y * u_y

        a = a_minus_p_x - dot_product * u_x
        b = a_minus_p_y - dot_product * u_y
        return math.sqrt(a * a + b * b)

    @staticmethod
    def is_point_above_line(origin: Point, angle: float, point: Point):
        min_angle = math.fmod(angle, math.pi)
        max_angle = min_angle + math.pi
        relative_point_angle = math.atan2(origin.y-point.y, origin.x-point.x)

        return not ((min_angle < relative_point_angle < max_angle) or relative_point_angle < max_angle - math.pi * 2)

    @staticmethod
    def _get_difference_vector(p1: Point, p2: Point) -> Point:
        return Point(p1.x - p2.x, p1.y - p2.y)

    @staticmethod
    def get_lines_within_box(origin: Point, angle: float, bounds: List[float]):
        x_min = bounds[0]
        y_min = bounds[1]
        x_max = bounds[2]
        y_max = bounds[3]

        x_min_intersection = Basic.get_intersection_point_of_line_with_x_axis(origin, angle, y_min)
        y_min_intersection = Basic.get_intersection_point_of_line_with_y_axis(origin, angle, x_min)
        x_max_intersection = Basic.get_intersection_point_of_line_with_x_axis(origin, angle, y_max)
        y_max_intersection = Basic.get_intersection_point_of_line_with_y_axis(origin, angle, x_max)

        p1 = None
        p2 = None

        if x_min_intersection is not None and x_min <= x_min_intersection <= x_max and (p1 is None or p2 is None):
            p = Point(x_min_intersection, y_min)
            if p1 is None:
                p1 = p
            else:
                p2 = p
        if x_max_intersection is not None and x_min <= x_max_intersection <= x_max and (p1 is None or p2 is None):
            p = Point(x_max_intersection, y_max)
            if p1 is None:
                p1 = p
            else:
                p2 = p
        if y_min_intersection is not None and y_min <= y_min_intersection <= y_max and (p1 is None or p2 is None):
            p = Point(x_min, y_min_intersection)
            if p1 is None:
                p1 = p
            else:
                p2 = p
        if y_max_intersection is not None and y_min <= y_max_intersection <= y_max and (p1 is None or p2 is None):
            p = Point(x_max, y_max_intersection)
            if p1 is None:
                p1 = p
            else:
                p2 = p

        if p1 is not None and p2 is not None:
            return LineString([[p1.x, p1.y], [p2.x, p2.y]])

        return None

        pass

    @staticmethod
    def get_intersection_point_of_line_with_y_axis(origin: Point, angle: float, y_axis_offset: float):
        return math.tan(angle) * (y_axis_offset - origin.x) + origin.y
        pass

    @staticmethod
    def get_intersection_point_of_line_with_x_axis(origin: Point, angle: float, x_axis_offset: float):
        if math.tan(angle) == 0:
            return None
        return 1 / math.tan(angle) * (x_axis_offset - origin.y) + origin.x
        pass
