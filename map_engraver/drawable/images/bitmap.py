from typing import Tuple, Optional

from pathlib import Path

from PIL import Image
from cairocffi import ImageSurface

from map_engraver.canvas import Canvas
from map_engraver.canvas.canvas_coordinate import CanvasCoordinate
from map_engraver.canvas.canvas_unit import CanvasUnit
from map_engraver.drawable.drawable import Drawable


class Bitmap(Drawable):
    path: Path
    bitmap_origin: CanvasCoordinate
    position: CanvasCoordinate
    width: Optional[CanvasUnit]
    height: Optional[CanvasUnit]
    rotation: float

    def __init__(self, path: Path):
        self.path = path
        self.image = Image.open(self.path)
        self.bitmap_origin = CanvasCoordinate.origin()
        self.position = CanvasCoordinate.origin()
        self.width = None
        self.height = None
        self.rotation = 0
        if self.image.format != 'PNG':
            raise NotImplementedError(
                'Bitmap formats other than PNG are not supported yet'
            )

    @property
    def bitmap_resolution(self) -> Tuple[int, int]:
        return self.image.size[0], self.image.size[1]

    @property
    def bitmap_size(self) -> Tuple[CanvasUnit, CanvasUnit]:
        pixels_per_inch = 96, 96
        if 'dpi' in self.image.info:
            pixels_per_inch = self.image.info['dpi']
        return (
            CanvasUnit.from_in(self.image.size[0] / pixels_per_inch[0]),
            CanvasUnit.from_in(self.image.size[1] / pixels_per_inch[1])
        )

    def draw(self, canvas: Canvas):
        # Images are rendered in points, despite the fact that images are
        # typically stored as pixels.
        surface = ImageSurface.create_from_png(
            self.path.as_posix()
        )
        resolution = self.bitmap_resolution
        size = self.bitmap_size
        canvas.context.save()
        canvas.context.translate(
            self.position.x.pt,
            self.position.y.pt
        )
        # In Cairocffi, by default, images are rendered in the scale of
        # 1 bitmap pixel = 1 canvas point.
        # This is counter-intuitive
        # canvas.context.scale(CanvasUnit.from_px(1).pt)
        canvas.context.rotate(self.rotation)
        canvas.context.scale(
            size[0].pt / resolution[0],
            size[1].pt / resolution[1]
        )
        canvas.context.translate(
            -self.bitmap_origin.x.px, -self.bitmap_origin.y.px
        )
        canvas.context.set_source_surface(surface, 0, 0)
        canvas.context.paint()
        canvas.context.restore()
