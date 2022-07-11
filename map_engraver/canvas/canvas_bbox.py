from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit


class CanvasBbox:
    pos: CanvasCoordinate
    width: CanvasUnit
    height: CanvasUnit

    def __init__(
            self,
            pos: CanvasCoordinate,
            width: CanvasUnit,
            height: CanvasUnit
    ):
        self.pos = pos
        self.width = width
        self.height = height

    @classmethod
    def from_pt(cls, x: float, y: float, w: float, h: float) -> 'CanvasBbox':
        return CanvasBbox(
            CanvasCoordinate.from_pt(x, y),
            CanvasUnit.from_pt(w),
            CanvasUnit.from_pt(h)
        )

    @classmethod
    def from_px(cls, x: float, y: float, w: float, h: float) -> 'CanvasBbox':
        return CanvasBbox(
            CanvasCoordinate.from_px(x, y),
            CanvasUnit.from_px(w),
            CanvasUnit.from_px(h)
        )

    @classmethod
    def from_in(cls, x: float, y: float, w: float, h: float) -> 'CanvasBbox':
        return CanvasBbox(
            CanvasCoordinate.from_in(x, y),
            CanvasUnit.from_in(w),
            CanvasUnit.from_in(h)
        )

    @classmethod
    def from_cm(cls, x: float, y: float, w: float, h: float) -> 'CanvasBbox':
        return CanvasBbox(
            CanvasCoordinate.from_cm(x, y),
            CanvasUnit.from_cm(w),
            CanvasUnit.from_cm(h)
        )

    @classmethod
    def from_mm(cls, x: float, y: float, w: float, h: float) -> 'CanvasBbox':
        return CanvasBbox(
            CanvasCoordinate.from_mm(x, y),
            CanvasUnit.from_mm(w),
            CanvasUnit.from_mm(h)
        )
