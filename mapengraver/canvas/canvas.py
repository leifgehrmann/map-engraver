from PIL import Image
from pathlib import Path

import cairocffi as cairo

from mapengraver.canvas.canvas_unit import CanvasUnit


class Canvas:
    height: float
    width: float
    dpi: int
    path_as_posix: str
    surface: cairo.surfaces.Surface
    context: cairo.context.Context

    def __init__(
            self,
            path: Path,
            surface_type: str,
            width: float,
            height: float,
            scale: float = 1
    ):
        self.path_as_posix = path.as_posix()

        if surface_type == 'pdf':
            surface = cairo.PDFSurface(
                self.path_as_posix,
                width,
                height
            )
        elif surface_type == 'svg':
            surface = cairo.SVGSurface(
                self.path_as_posix,
                width,
                height
            )
        elif surface_type == 'png':
            surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32,
                int(width),
                int(height)
            )
        else:
            raise Exception('Unexpected Format: %s' % surface_type)

        context = cairo.Context(surface)

        self.width = width
        self.height = height
        self.scale = scale
        self.surface = surface
        self.context = context

        self.context.scale(self.scale, self.scale)

    def set_antialias_mode(self, antialias_mode: int):
        self.context.set_antialias(antialias_mode)

    def close(self):
        # Special edge case for ImageSurfaces
        if isinstance(self.surface, cairo.ImageSurface):
            self.surface.write_to_png(self.path_as_posix)

        self.surface.finish()

        # Cairo sets the dots-per-image as 72 pixels-per-inch, when it should
        # be 96. We also want to take into account the scale, since the number
        # of inches should not change. We use Pillow to adjust the DPI.
        if isinstance(self.surface, cairo.ImageSurface):
            image = Image.open(self.path_as_posix)
            dpi = CanvasUnit.from_in(1).pt * self.scale
            image.save(self.path_as_posix, dpi=(dpi, dpi))
