from typing import Tuple

from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit


class CanvasBbox:
    min_pos: CanvasCoordinate
    max_pos: CanvasCoordinate

    def __init__(
            self,
            min_pos: CanvasCoordinate,
            max_pos: CanvasCoordinate
    ):
        self.min_pos = min_pos
        self.max_pos = max_pos

        if self.min_pos.x > self.max_pos.x:
            raise Exception('min_pos.x cannot be greater than max_pos.x')
        if self.min_pos.y > self.max_pos.y:
            raise Exception('min_pos.y cannot be greater than max_pos.y')

    @property
    def width(self) -> CanvasUnit:
        return self.max_pos.x - self.min_pos.x

    @property
    def height(self) -> CanvasUnit:
        return self.max_pos.y - self.min_pos.y

    @property
    def bounds(self) -> Tuple[CanvasUnit, CanvasUnit, CanvasUnit, CanvasUnit]:
        """Returns the bounding region as a tuple (minx, miny, maxx, maxy)"""
        return (
            self.min_pos.x,
            self.min_pos.y,
            self.max_pos.x,
            self.max_pos.y
        )

    @classmethod
    def from_size(
        cls,
        x: CanvasUnit,
        y: CanvasUnit,
        w: CanvasUnit,
        h: CanvasUnit
    ) -> 'CanvasBbox':
        return CanvasBbox(
            CanvasCoordinate(x, y),
            CanvasCoordinate(x + w, y + h)
        )

    @classmethod
    def from_size_pt(
        cls,
        x: float,
        y: float,
        w: float,
        h: float
    ) -> 'CanvasBbox':
        return CanvasBbox(
            CanvasCoordinate.from_pt(x, y),
            CanvasCoordinate.from_pt(x + w, y + h)
        )

    @classmethod
    def from_size_px(
            cls,
            x: float,
            y: float,
            w: float,
            h: float
    ) -> 'CanvasBbox':
        return CanvasBbox(
            CanvasCoordinate.from_px(x, y),
            CanvasCoordinate.from_px(x + w, y + h)
        )

    @classmethod
    def from_size_in(
            cls,
            x: float,
            y: float,
            w: float,
            h: float
    ) -> 'CanvasBbox':
        return CanvasBbox(
            CanvasCoordinate.from_in(x, y),
            CanvasCoordinate.from_in(x + w, y + h)
        )

    @classmethod
    def from_size_cm(
            cls,
            x: float,
            y: float,
            w: float,
            h: float
    ) -> 'CanvasBbox':
        return CanvasBbox(
            CanvasCoordinate.from_cm(x, y),
            CanvasCoordinate.from_cm(x + w, y + h)
        )

    @classmethod
    def from_size_mm(
            cls,
            x: float,
            y: float,
            w: float,
            h: float
    ) -> 'CanvasBbox':
        return CanvasBbox(
            CanvasCoordinate.from_mm(x, y),
            CanvasCoordinate.from_mm(x + w, y + h)
        )
