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
