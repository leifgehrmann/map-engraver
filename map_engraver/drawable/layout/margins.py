from shapely.geometry import Polygon
from typing import Optional

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.drawable import Drawable
from map_engraver.graphicshelper import CairoHelper


class Margins(Drawable):
    stroke_width: Optional[CanvasUnit]
    margin_bottom: Optional[CanvasUnit]
    margin_top: Optional[CanvasUnit]
    margin_right: Optional[CanvasUnit]
    margin_left: Optional[CanvasUnit]

    def __init__(self):
        self.margin_left = None
        self.margin_right = None
        self.margin_top = None
        self.margin_bottom = None
        self.fill_color = (1, 1, 1, 1)
        self.stroke_color = (0, 0, 0, 1)
        self.stroke_width = None

    def set_margins(self, margin: CanvasUnit):
        self.margin_left = margin
        self.margin_right = margin
        self.margin_top = margin
        self.margin_bottom = margin

    def draw(self, canvas: Canvas):
        min_x = self.margin_left.pt
        min_y = self.margin_top.pt
        max_x = canvas.width - self.margin_right.pt
        max_y = canvas.height - self.margin_bottom.pt

        exterior_shape = Polygon(
            [
                (0, 0),
                (canvas.width, 0),
                (canvas.width, canvas.height),
                (0, canvas.height),
                (0, 0)
            ],
            [
                list(reversed([
                    (min_x, min_y),
                    (max_x, min_y),
                    (max_x, max_y),
                    (min_x, max_y),
                    (min_x, min_y)
                ]))
            ]
        )

        if self.stroke_width is not None:
            interior_outline = Polygon([
                (min_x, min_y),
                (max_x, min_y),
                (max_x, max_y),
                (min_x, max_y),
                (min_x, min_y)
            ])
            canvas.context.set_line_width(self.stroke_width.pt)
            canvas.context.set_source_rgba(*self.stroke_color)
            CairoHelper.draw_polygon(canvas.context, interior_outline)
            canvas.context.stroke()

        canvas.context.set_source_rgba(*self.fill_color)
        CairoHelper.draw_polygon(canvas.context, exterior_shape)
        canvas.context.fill()
