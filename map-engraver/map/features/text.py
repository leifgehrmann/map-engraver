from cairocffi import Context
from shapely.geometry import LineString
from graphicshelper import CairoHelper
import math


class Text:

    def __init__(self, text: str, line_string: LineString):
        self.text = text
        self.line_string = line_string

        self.text_height = 1
        self.text_style = None  # Todo
        self.text_alignment = 'center'
        self.text_alignment_offset = 0
        self.text_spacing = 0
        self.text_spacing_sequence = None  # Todo
        self.line_text_offset = 0
        self.force_upside_down = False
        self.debug = False

    def set_text_height(self, text_height):
        self.text_height = text_height
        return self

    def set_text_alignment(self, text_alignment):
        self.text_alignment = text_alignment
        return self

    def set_text_spacing(self, text_spacing):
        self.text_spacing = text_spacing
        return self

    def set_line_text_offset(self, line_text_offset):
        self.line_text_offset = line_text_offset
        return self

    def set_force_upside_down(self, force_upside_down):
        self.force_upside_down = force_upside_down
        return self

    @staticmethod
    def parallel_offset(line_string, distance):
        tls = line_string.parallel_offset(distance)
        if distance <= 0:
            return tls
        else:
            return LineString(reversed(tls.coords))

    def get_text_baseline(self, ctx):
        bottom_offset = self.text_height / 2 + self.line_text_offset
        top_offset = -self.text_height / 2 + self.line_text_offset
        line_string_right = Text.parallel_offset(self.line_string, bottom_offset)
        line_string_left = Text.parallel_offset(self.line_string, top_offset)

        center_start_pos = self.line_string.interpolate(0)
        right_start_pos = line_string_right.interpolate(0)
        left_start_pos = line_string_left.interpolate(0)

        reverse_lines = math.atan2(left_start_pos.y - right_start_pos.y, left_start_pos.x - right_start_pos.x) < 0
        if self.force_upside_down:
            reverse_lines = not reverse_lines

        if reverse_lines:
            bottom_offset = self.text_height / 2 - self.line_text_offset
            top_offset = -self.text_height / 2 - self.line_text_offset
            line_string_right = Text.parallel_offset(self.line_string, bottom_offset)
            line_string_left = Text.parallel_offset(self.line_string, top_offset)

            line_string_right = LineString(reversed(line_string_right.coords))
            line_string_left = LineString(reversed(line_string_left.coords))

            temp = line_string_right
            line_string_right = line_string_left
            line_string_left = temp

            center_start_pos = self.line_string.interpolate(0)
            right_start_pos = line_string_right.interpolate(0)
            left_start_pos = line_string_left.interpolate(0)

        if self.debug:
            ctx.set_line_width(0.1)
            ctx.set_source_rgba(0, 1, 0, 0.5)
            CairoHelper.draw_point(ctx, center_start_pos, 0.5)
            CairoHelper.draw_line_string(ctx, self.line_string)
            ctx.stroke()
            ctx.set_source_rgba(0, 1, 1, 0.5)
            CairoHelper.draw_point(ctx, right_start_pos, 0.5)
            CairoHelper.draw_line_string(ctx, line_string_right)
            ctx.stroke()
            ctx.set_source_rgba(0, 0, 0, 0.5)
            CairoHelper.draw_point(ctx, left_start_pos, 0.5)
            CairoHelper.draw_line_string(ctx, line_string_left)
            ctx.stroke()

        return line_string_left

    def draw(self, ctx: Context):

        text_baseline = self.get_text_baseline(ctx)

        default_font_max_height = ctx.get_scaled_font().extents()[0]

        text_max_length = float('inf')
        line_string_bottom_length = text_baseline.length

        trimmed = False
        while text_max_length > line_string_bottom_length:
            text_max_length = ctx.text_extents(self.text)[4] / default_font_max_height * self.text_height + \
                              (len(self.text)-1) * self.text_spacing
            if text_max_length > line_string_bottom_length:
                self.text = self.text[:-1].strip()
                trimmed = True

        text_start_interp_pos_min = 0
        text_start_interp_pos_max = line_string_bottom_length - text_max_length
        if self.text_alignment == 'left':
            text_start_interp_pos = self.text_alignment_offset
        elif self.text_alignment == 'center':
            text_start_interp_pos = line_string_bottom_length / 2 - text_max_length / 2 - self.text_alignment_offset
        else:
            text_start_interp_pos = line_string_bottom_length - text_max_length - self.text_alignment_offset
        text_start_interp_pos = min(text_start_interp_pos_max, max(text_start_interp_pos_min, text_start_interp_pos))

        text_interp_pos = text_start_interp_pos
        for char in self.text:
            char_pos_origin = text_baseline.interpolate(text_interp_pos)
            char_advance_x = ctx.text_extents(char)[4] / default_font_max_height * self.text_height
            char_pos_end = text_baseline.interpolate(text_interp_pos + char_advance_x)

            ctx.save()
            ctx.translate(char_pos_origin.x, char_pos_origin.y)
            text_angle = math.atan2(char_pos_end.y - char_pos_origin.y, char_pos_end.x - char_pos_origin.x)
            ctx.rotate(text_angle)
            ctx.scale(1 / default_font_max_height * self.text_height)
            if not trimmed:
                ctx.set_source_rgba(0, 0, 0, 1)
            else:
                ctx.set_source_rgba(0, 0, 1, 1)
            ctx.show_text(char)
            ctx.fill()
            ctx.restore()

            text_interp_pos += char_advance_x + self.text_spacing
