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
        self.bitmap_origin = CanvasCoordinate.origin()
        self.position = CanvasCoordinate.origin()
        self.width = None
        self.height = None
        self.rotation = 0

    def read_bitmap_size(self) -> Tuple[CanvasUnit, CanvasUnit]:
        image = Image.open(self.path)
        if image.format != 'PNG':
            raise NotImplementedError(
                'Bitmap formats other than PNG are not supported yet'
            )
        return (
            CanvasUnit.from_px(image.size[0]),
            CanvasUnit.from_px(image.size[1])
        )

    def draw(self, canvas: Canvas):
        image = Image.open(self.path)
        if image.format != 'PNG':
            raise NotImplementedError(
                'Bitmap formats other than PNG are not supported yet'
            )
        # Images are rendered in points, despite the fact that images are
        # typically stored as pixels.
        surface = ImageSurface.create_from_png(
            self.path.as_posix()
        )
        bmp_width = surface.get_width()
        bmp_height = surface.get_height()
        canvas.context.save()
        canvas.context.translate(
            self.position.x.pt,
            self.position.y.pt
        )
        canvas.context.scale(CanvasUnit.from_pt(1).px)
        canvas.context.rotate(self.rotation)
        # if self.width is not None and \
        #         self.height is not None:
        #     svg_surface.set_width(self.width.pt, preserve_ratio=False)
        #     svg_surface.set_height(self.height.pt, preserve_ratio=False)
        # elif self.width is not None:
        #     svg_surface.set_width(self.width.pt, preserve_ratio=True)
        # elif self.height is not None:
        #     svg_surface.set_height(self.height.pt, preserve_ratio=True)
        canvas.context.scale(self.width / bmp_width, self.height / bmp_height)
        canvas.context.translate(
            -self.bitmap_origin.x.px, -self.bitmap_origin.y.px
        )
        canvas.context.set_source_surface(surface, 0, 0)
        canvas.context.paint()
        canvas.context.restore()
