from typing import Tuple, Optional

from pathlib import Path

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.drawable import Drawable
from map_engraver.graphicshelper.svg_surface import SvgSurface


class Svg(Drawable):
    path: Path
    svg_origin: CanvasCoordinate
    position: CanvasCoordinate
    width: Optional[CanvasUnit]
    height: Optional[CanvasUnit]
    rotation: float

    def __init__(self, path: Path):
        self.path = path
        self.svg_origin = CanvasCoordinate.origin()
        self.position = CanvasCoordinate.origin()
        self.width = None
        self.height = None
        self.rotation = 0

    def read_svg_size(self) -> Tuple[CanvasUnit, CanvasUnit]:
        svg_surface = SvgSurface(self.path)
        return (
            CanvasUnit.from_pt(svg_surface.svg_width),
            CanvasUnit.from_pt(svg_surface.svg_height)
        )

    def draw(self, canvas: Canvas):
        svg_surface = SvgSurface(self.path)
        svg_surface.set_origin(*self.svg_origin.pt)
        svg_surface.set_rotation(self.rotation)
        svg_surface.set_translation(*self.position.pt)
        if self.width is not None and \
                self.height is not None:
            svg_surface.set_width(self.width.pt, preserve_ratio=False)
            svg_surface.set_height(self.height.pt, preserve_ratio=False)
        elif self.width is not None:
            svg_surface.set_width(self.width.pt, preserve_ratio=True)
        elif self.height is not None:
            svg_surface.set_height(self.height.pt, preserve_ratio=True)
        svg_surface.draw(canvas.context, canvas.surface)
