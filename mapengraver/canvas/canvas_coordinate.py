from typing import Tuple

from mapengraver.canvas.canvas_unit import CanvasUnit


class CanvasCoordinate:
    x: CanvasUnit
    y: CanvasUnit

    def __init__(self, x: CanvasUnit, y:CanvasUnit):
        self.x = x
        self.y = y

    @property
    def pt(self) -> Tuple[float, float]:
        return self.x.pt, self.y.pt

    @staticmethod
    def origin():
        """Returns the top left coordinate of the canvas"""
        return CanvasCoordinate(x=CanvasUnit(0), y=CanvasUnit(0))
