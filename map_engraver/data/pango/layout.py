from typing import Optional, Tuple

import pangocairocffi
import pangocffi
from pangocffi import Layout as PangoLayout, Alignment

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_bbox import CanvasBbox
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit


class Layout:
    def __init__(self, canvas: Canvas):
        self._layout = pangocairocffi.create_layout(canvas.context)
        self._position = CanvasCoordinate.origin()
        self._color = (0, 0, 0, 1)

    @property
    def pango_layout(self) -> PangoLayout:
        return self._layout

    @property
    def width(self) -> Optional[CanvasUnit]:
        pango_width = self._layout.width
        if pango_width == -1:
            return None
        return CanvasUnit.from_pt(pangocffi.units_to_double(pango_width))

    @width.setter
    def width(self, x: CanvasUnit):
        self._layout.width = pangocffi.units_from_double(x.pt)

    def reset_width(self):
        self._layout.width = -1

    @property
    def logical_extents(self) -> CanvasBbox:
        extent = self._layout.get_extents()[1]
        x = CanvasUnit.from_pt(pangocffi.units_to_double(extent.x))
        y = CanvasUnit.from_pt(pangocffi.units_to_double(extent.y))
        x += self._position.x
        y += self._position.y
        width = CanvasUnit.from_pt(pangocffi.units_to_double(extent.width))
        height = CanvasUnit.from_pt(pangocffi.units_to_double(extent.height))
        return CanvasBbox.from_size(x, y, width, height)

    @property
    def height(self) -> Optional[CanvasUnit]:
        pango_height = self._layout.height
        if pango_height == -1:
            return None
        return CanvasUnit.from_pt(pangocffi.units_to_double(pango_height))

    @height.setter
    def height(self, x: CanvasUnit):
        self._layout.height = pangocffi.units_from_double(x.pt)

    def reset_height(self):
        self._layout.height = -1

    @property
    def alignment(self) -> Alignment:
        return self._layout.alignment

    @alignment.setter
    def alignment(self, x: Alignment):
        self._layout.alignment = x

    @property
    def text(self) -> str:
        return self._layout.text

    @text.setter
    def text(self, text: str):
        self._layout.text = text

    def apply_markup(self, markup: str):
        self._layout.apply_markup(markup)

    @property
    def position(self) -> CanvasCoordinate:
        return self._position

    @position.setter
    def position(self, position: CanvasCoordinate):
        self._position = position

    @property
    def color(self) -> Tuple[float, float, float, float]:
        return self._color

    @color.setter
    def color(self, color: Tuple[float, float, float, float]):
        self._color = color
