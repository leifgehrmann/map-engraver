from typing import Tuple

from mapengraver.canvas import Canvas
from mapengraver.canvas.canvas_unit import CanvasUnit
from mapengraver.drawable.drawable import Drawable
from mapengraver.graphicshelper import CairoHelper
from mapengraver.logging.progressable import ProgressObservable

from shapely.geometry import Polygon


class UnitScale(Drawable, ProgressObservable):
    color: Tuple[int, int, int]

    def __init__(self):
        self.color = (0, 0, 0)
        self.translation_offset = (0, 0)

    def progress(self):
        pass

    def draw(self, canvas: Canvas):
        units = ['px', 'pt', 'mm', 'cm', 'in']
        offset = 0
        for unit in units:
            self.draw_rectangle(canvas, offset, unit)
            offset += 1

    def draw_rectangle(self, canvas: Canvas, offset: int, unit: str):
        height = CanvasUnit.from_pt(10).pt
        width = CanvasUnit.from_unit(1, unit).pt
        offset_height = height * offset
        top_left = (0, offset_height)
        top_right = (width, offset_height)
        bottom_left = (0, offset_height + height)
        bottom_right = (width, offset_height + height)

        shape = Polygon([
            top_left,
            top_right,
            bottom_right,
            bottom_left,
            top_left
        ])

        canvas.context.set_source_rgba(*self.color)
        CairoHelper.draw_polygon(canvas.context, shape)
        canvas.context.set_source_rgba(0.5, 0.5, 0.5, 1)
        canvas.context.fill()
