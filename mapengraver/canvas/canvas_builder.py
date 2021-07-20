from typing import Optional

import cairocffi as cairo
from pathlib import Path

from mapengraver.canvas import Canvas
from mapengraver.canvas.canvas_unit import CanvasUnit


class CanvasBuilder:
    path: Optional[Path]
    width: Optional[CanvasUnit]
    height: Optional[CanvasUnit]
    pixel_scale_factor: float
    surface_type: Optional[str]
    antialias_mode: int

    def __init__(self):
        self.path = None
        self.width = None
        self.height = None
        self.pixel_scale_factor = 1
        self.surface_type = None
        self.antialias_mode = cairo.ANTIALIAS_DEFAULT

    def build(self) -> Canvas:
        self.validate_path()
        self.validate_pixel_scale_factor()
        self.validate_size()

        pixel_scale = self._calculate_pixel_scale_factor()
        width_in_points = self.width.pt * pixel_scale
        height_in_points = self.height.pt * pixel_scale

        canvas = Canvas(
            self.path,
            self.surface_type,
            width_in_points,
            height_in_points,
        )

        canvas.set_scale(pixel_scale)
        canvas.set_antialias_mode(self.antialias_mode)

        return canvas

    def set_path(self, path: Path) -> None:
        self.path = path
        file_extension = path.suffix
        file_extension = file_extension.lower()
        if file_extension == '.png':
            self.surface_type = 'png'
        elif file_extension == '.svg':
            self.surface_type = 'svg'
        elif file_extension == '.pdf':
            self.surface_type = 'pdf'
        else:
            raise RuntimeError('Unknown file type: %s' % file_extension)

    def set_size(self, width: CanvasUnit, height: CanvasUnit):
        if width.pt <= 0:
            raise RuntimeError('Invalid width: %s pt' % self.width.pt)
        if height.pt <= 0:
            raise RuntimeError('Invalid height: %s pt' % self.height.pt)
        self.width = width
        self.height = height

    def set_pixel_scale_factor(self, pixel_scale_factor) -> None:
        """
        Sets the pixel scale factor. This is useful if one wants to achieve
        graphics that look pixel perfect on high-DPI displays or
        "Retina-Displays".

        :param pixel_scale_factor:
            For example: `2` to scale the image twice as large. `0.5` for an
            image half the size.
        """
        self.pixel_scale_factor = pixel_scale_factor

    def set_anti_alias_mode(self, antialias_mode):
        if antialias_mode < 0 or antialias_mode > 6:
            raise RuntimeError(
                'Invalid antialias mode: %d' % self.antialias_mode
            )
        self.antialias_mode = antialias_mode

    def validate_path(self):
        if not self.path.parents[0].is_dir():
            raise RuntimeError('Not such file or directory: %s' % self.path)

    def validate_size(self):
        if self.width is None or self.height is None:
            raise RuntimeError('Invalid size: None, None')

    def validate_pixel_scale_factor(self):
        if self.is_surface_type_vector() and self.pixel_scale_factor != 1:
            raise RuntimeError(
                'Scale other than 1 cannot be set for vector surface types: '
                '%s' % self.surface_type
            )

    def is_surface_type_vector(self) -> bool:
        return self.surface_type in ['svg', 'pdf']

    def _calculate_pixel_scale_factor(self) -> float:
        if self.is_surface_type_vector():
            return 1
        return CanvasUnit.from_pt(1).px * self.pixel_scale_factor
