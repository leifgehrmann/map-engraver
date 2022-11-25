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
    def bitmap_pixel_size(self) -> Tuple[int, int]:
        return self.image.size[0], self.image.size[1]

    @property
    def bitmap_size(self) -> Tuple[CanvasUnit, CanvasUnit]:
        # Default resolution in cairocffi is 96 pixels per inch.
        x_resolution, y_resolution = 96, 96

        # According to https://exiftool.org/TagNames/EXIF.html:
        # 282 = 0x011a = XResolution
        # 283 = 0x011b = YResolution
        exif = self.image.getexif()
        if 282 in exif:
            x_resolution = exif[282]
        if 283 in exif:
            y_resolution = exif[283]

        return (
            CanvasUnit.from_in(self.image.size[0] / x_resolution),
            CanvasUnit.from_in(self.image.size[1] / y_resolution)
        )

    def draw(self, canvas: Canvas):
        # Images are rendered in points, despite the fact that images are
        # typically stored as pixels.
        surface = ImageSurface.create_from_png(
            self.path.as_posix()
        )
        pixel_size = self.bitmap_pixel_size
        size = self.bitmap_size
        canvas.context.save()
        canvas.context.translate(
            self.position.x.pt,
            self.position.y.pt
        )
        canvas.context.rotate(self.rotation)

        scale_x = 1
        scale_y = 1
        if self.width is not None and \
                self.height is not None:
            scale_x = self.width.pt / size[0].pt
            scale_y = self.height.pt / size[1].pt
        elif self.width is not None:
            scale_x = self.width.pt / size[0].pt
            scale_y = scale_x
        elif self.height is not None:
            scale_y = self.height.pt / size[1].pt
            scale_x = scale_y
        canvas.context.scale(scale_x, scale_y)

        canvas.context.scale(
            size[0].pt / pixel_size[0],
            size[1].pt / pixel_size[1]
        )

        canvas.context.translate(
            -self.bitmap_origin.x.px, -self.bitmap_origin.y.px
        )

        canvas.context.set_source_surface(surface, 0, 0)
        canvas.context.paint()
        canvas.context.restore()
