from typing import Tuple

from map_engraver.canvas.canvas_unit import CanvasUnit


class CanvasCoordinate:
    x: CanvasUnit
    y: CanvasUnit

    def __init__(self, x: CanvasUnit, y: CanvasUnit):
        self.x = x
        self.y = y

    @property
    def pt(self) -> Tuple[float, float]:
        return self.x.pt, self.y.pt

    @classmethod
    def from_pt(cls, x: float, y: float) -> 'CanvasCoordinate':
        return CanvasCoordinate(CanvasUnit.from_pt(x), CanvasUnit.from_pt(y))

    @property
    def inches(self) -> Tuple[float, float]:
        return self.x.inches, self.y.inches

    @classmethod
    def from_in(cls, x: float, y: float) -> 'CanvasCoordinate':
        return CanvasCoordinate(CanvasUnit.from_in(x), CanvasUnit.from_in(y))

    @property
    def mm(self) -> Tuple[float, float]:
        return self.x.mm, self.y.mm

    @classmethod
    def from_mm(cls, x: float, y: float) -> 'CanvasCoordinate':
        return CanvasCoordinate(CanvasUnit.from_mm(x), CanvasUnit.from_mm(y))

    @property
    def cm(self) -> Tuple[float, float]:
        return self.x.cm, self.y.cm

    @classmethod
    def from_cm(cls, x: float, y: float) -> 'CanvasCoordinate':
        return CanvasCoordinate(CanvasUnit.from_cm(x), CanvasUnit.from_cm(y))

    @property
    def px(self) -> Tuple[float, float]:
        return self.x.px, self.y.px

    @classmethod
    def from_px(cls, x: float, y: float) -> 'CanvasCoordinate':
        return CanvasCoordinate(CanvasUnit.from_px(x), CanvasUnit.from_px(y))

    @staticmethod
    def origin() -> 'CanvasCoordinate':
        """Returns the top left coordinate of the canvas"""
        return CanvasCoordinate(x=CanvasUnit(0), y=CanvasUnit(0))
