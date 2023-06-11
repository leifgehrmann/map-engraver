from typing import Union, List, Tuple, Optional

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.data.pango.layout import Layout
from map_engraver.drawable.drawable import Drawable
from map_engraver.graphicshelper.autotrace_text import AutotraceText
from map_engraver.graphicshelper.cairo_svg_helper import CairoSvgHelper


class PangoStrokeDrawer(Drawable):
    stroke_width: Optional[CanvasUnit]
    stroke_color: Optional[Tuple[float, float, float, float]]
    stroke_line_cap: Optional[int]  # See cairocffi constants: LINE_CAP_*
    stroke_line_join: Optional[int]  # See cairocffi constants: LINE_JOIN_*
    pango_objects: List[Union[Layout]]

    def __init__(self):
        self.objects = []
        self.stroke_color = (0, 0, 0, 1)
        self.stroke_width = CanvasUnit.from_pt(1)
        self.stroke_line_cap = None
        self.stroke_line_join = None

    def draw(self, canvas: Canvas):
        if self.stroke_width is not None:
            canvas.context.set_line_width(self.stroke_width.pt)
        if self.stroke_color is not None:
            canvas.context.set_source_rgba(*self.stroke_color)
        if self.stroke_line_cap is not None:
            canvas.context.set_line_cap(self.stroke_line_cap)
        if self.stroke_line_join is not None:
            canvas.context.set_line_join(self.stroke_line_join)

        for pango_object in self.pango_objects:
            canvas.context.save()
            canvas.context.translate(*pango_object.position.pt)

            layout = pango_object.pango_layout
            commands = AutotraceText.convert_pango_layout_to_svg_draw_commands(
                layout
            )
            CairoSvgHelper.execute_svg_path_in_cairo(
                canvas.context,
                commands
            )
            canvas.context.stroke()
            canvas.context.restore()
