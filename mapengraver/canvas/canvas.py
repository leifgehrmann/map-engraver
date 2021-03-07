from pathlib import Path

import cairocffi as cairo


class Canvas:
    height: float
    width: float
    path_as_posix: str
    surface: cairo.surfaces.Surface
    context: cairo.context.Context

    def __init__(
            self,
            path: Path,
            surface_type: str,
            width: float,
            height: float
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
        self.surface = surface
        self.context = context

    def set_scale(self, scale: float):
        self.context.scale(scale, scale)

    def set_antialias_mode(self, antialias_mode: int):
        self.context.set_antialias(antialias_mode)

    def close(self):
        # Special edge case for ImageSurfaces
        if isinstance(self.surface, cairo.ImageSurface):
            self.surface.write_to_png(self.path_as_posix)

        self.surface.finish()
