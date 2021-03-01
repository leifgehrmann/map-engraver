from typing import Optional

import cairocffi as cairo
from pathlib import Path

from mapengraver.canvas import Canvas

pixels_per_point = 0.75
points_per_inch = 72
mm_per_inch = 25.4
points_per_pixel = 1 / pixels_per_point
inch_per_mm = 1 / mm_per_inch


class CanvasBuilder:
    path: Optional[Path]
    width: Optional[float]
    height: Optional[float]
    pixel_scale_factor: float
    surface_type: Optional[str]
    antialias_mode: int

    def __init__(self):
        self.path = None
        self.width = None
        self.height = None
        self.units = None
        self.pixel_scale_factor = 1
        self.surface_type = None
        self.antialias_mode = cairo.ANTIALIAS_DEFAULT

    def build(self) -> Canvas:
        self.validate_path()
        self.validate_pixel_scale_factor()
        self.validate_size()
        self.validate_surface_type()
        self.validate_antialias_mode()

        canvas_scale = self._calculate_units_in_points()
        width_in_points = self.width * canvas_scale
        height_in_points = self.height * canvas_scale

        canvas = Canvas(
            self.path,
            self.surface_type,
            width_in_points,
            height_in_points,
        )

        canvas.set_scale(canvas_scale)
        canvas.set_antialias_mode(self.antialias_mode)

        return canvas

    def set_path(self, path: Path) -> None:
        self.path = path
        file_extension = path.suffix
        file_extension = file_extension.lower()
        print(file_extension)
        if self.surface_type is None and file_extension != '':
            if file_extension == '.png':
                self.surface_type = 'png'
            elif file_extension == '.svg':
                self.surface_type = 'svg'
            elif file_extension == '.pdf':
                self.surface_type = 'pdf'

    def set_surface_type(self, surface_type: str) -> None:
        self.surface_type = surface_type

    def set_size(self, width, height, units):
        self.width = width
        self.height = height
        self.units = units

    def set_pixel_scale_factor(self, pixel_scale_factor):
        self.pixel_scale_factor = pixel_scale_factor

    def validate_path(self):
        if not self.path.parents[0].is_dir():
            raise RuntimeError('Not such file or directory: %s' % self.path)

    def validate_size(self):
        if self.width is None:
            raise RuntimeError('Invalid width: None')
        if self.height is None:
            raise RuntimeError('Invalid height: None')
        if self.width <= 0:
            raise RuntimeError('Invalid width: %s' % self.width)
        if self.height < 0:
            raise RuntimeError('Invalid height: %s' % self.surface_type)

    def validate_units(self):
        if self.units not in ['px', 'mm', 'in', 'pt']:
            raise RuntimeError('Invalid units: %s' % self.units)

    def validate_pixel_scale_factor(self):
        if self.is_surface_type_vector() and self.pixel_scale_factor != 1:
            raise RuntimeError(
                'Scale other than 1 cannot be set for vector surface types: '
                '%s' % self.surface_type
            )

    def validate_antialias_mode(self):
        if self.antialias_mode < 0 or self.antialias_mode > 6:
            raise RuntimeError(
                'Invalid antialias mode: %d' % self.antialias_mode
            )

    def validate_surface_type(self):
        if self.surface_type not in ['pdf', 'png', 'svg']:
            raise RuntimeError('Invalid surface type: %s' % self.surface_type)

    def is_surface_type_vector(self) -> bool:
        return self.surface_type in ['svg', 'pdf']

    def _calculate_units_in_points(self) -> float:
        if self.units == 'pt':
            return 1.0
        if self.units == 'in':
            return points_per_inch
        if self.units == 'mm':
            return inch_per_mm * points_per_inch
        if self.units == 'px':
            return points_per_pixel * self.pixel_scale_factor
