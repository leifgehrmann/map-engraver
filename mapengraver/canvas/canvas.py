import os

from typing import Tuple

import cairocffi as cairo


class Canvas:
    dpi: int
    height: int
    width: int
    file_format: str

    def __init__(self, file_format: str, width: int, height: int, dpi: int):
        self.file_format = file_format
        self.width = width
        self.height = height
        self.dpi = dpi

    def _create_map_surface(self) -> Tuple[cairo.Surface, cairo.Context]:
        pixels_per_point = 0.75
        points_per_inch = 72
        mm_per_inch = 25.4

        canvas_dimensions = self.map_config.get_canvas_unit_dimensions()
        canvas_width, canvas_height = canvas_dimensions
        canvas_format = self.map_config.get_canvas_format()
        canvas_scale = 1

        if canvas_format in ['pdf', 'ps']:
            canvas_width *= points_per_inch
            canvas_height *= points_per_inch
            canvas_scale *= points_per_inch

            if self.map_config.get_canvas_units() == 'pt':
                canvas_width /= points_per_inch
                canvas_height /= points_per_inch
                canvas_scale /= points_per_inch
            elif self.map_config.get_canvas_units() == 'mm':
                canvas_width /= mm_per_inch
                canvas_height /= mm_per_inch
                canvas_scale /= mm_per_inch
        else:
            canvas_width *= self.map_config.get_canvas_pixels_per_unit()
            canvas_height *= self.map_config.get_canvas_pixels_per_unit()
            canvas_scale *= self.map_config.get_canvas_pixels_per_unit()

            if self.map_config.get_canvas_units() != 'px':
                canvas_width *= pixels_per_point
                canvas_height *= pixels_per_point
                canvas_scale *= pixels_per_point

        output_directory = self.map_config.get_output_directory()
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        output_filepath = self._get_output_filepath()

        if canvas_format == 'pdf':
            surface = cairo.PDFSurface(
                output_filepath,
                canvas_width,
                canvas_height
            )
        elif canvas_format == 'svg':
            surface = cairo.SVGSurface(
                output_filepath,
                canvas_width,
                canvas_height
            )
        elif canvas_format == 'png':
            surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32,
                int(canvas_width),
                int(canvas_height)
            )
        else:
            raise Exception('Unexpected Format: %s' % canvas_format)

        context = cairo.Context(surface)

        context.scale(canvas_scale, canvas_scale)  # Normalizing the canvas

        antialias_mode = self.map_config.get_canvas_antialias_mode()
        if antialias_mode == 'default':
            context.set_antialias(cairo.ANTIALIAS_DEFAULT)
        elif antialias_mode == 'none':
            context.set_antialias(cairo.ANTIALIAS_NONE)
        else:
            raise Exception('Unexpected antialias mode: %s' % antialias_mode)

        return surface, context
