from typing import Tuple

from mapengraver.canvas import Canvas
from mapengraver.drawable.drawable import Drawable
from mapengraver.graphicshelper import CairoHelper

from shapely.geometry import Polygon


class Background(Drawable):
    color: Tuple[int, int, int]

    def __init__(self):
        self.color = (0, 0, 0)

    def draw(self, canvas: Canvas):
        top_left = (0, 0)
        top_right = (canvas.width, 0)
        bottom_left = (0, canvas.height)
        bottom_right = (canvas.width, canvas.height)

        background_shape = Polygon([
            top_left,
            top_right,
            bottom_right,
            bottom_left,
            top_left
        ])

        canvas.context.set_source_rgba(*self.color)
        CairoHelper.draw_polygon(canvas.context, background_shape)
        canvas.context.fill()
