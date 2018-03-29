import os
from typing import Union, Tuple

from graphicshelper import SvgSurface
from map.layer import Sublayer
from map.layer.ilayer import ILayer


class SvgLayer(Sublayer):

    @staticmethod
    def create_from_dict(data: dict, parent: ILayer) -> 'SvgLayer':
        layer = SvgLayer().set_parent(parent)
        if 'file' in data:
            svg_file_path = os.path.join(parent.get_relative_directory(), data['file'])
            layer.set_svg_file(svg_file_path)
        if 'dimension' in data:
            layer.set_dimensions(data['dimension'])
        if 'position' in data:
            layer.set_position(data['position'])
        return layer

    def __init__(self):
        self.svg_file = None
        self.svg_surface = None
        self.position = [0, 0]
        self.dimensions = [None, None]

    def set_svg_file(self, svg_file: str) -> 'SvgLayer':
        self.svg_file = svg_file
        self.svg_surface = SvgSurface(self.svg_file)
        return self

    def set_position(self, position: Tuple[float, float]) -> 'SvgLayer':
        self.position = position
        return self

    def set_dimensions(self, dimensions: Tuple[Union[float, None], Union[float, None]]) -> 'SvgLayer':
        self.dimensions = dimensions
        return self

    def draw(self):
        if not isinstance(self.svg_surface, SvgSurface):
            # Todo: Throw error or display error here
            return

        # Set dimensions
        if self.dimensions[0] is not None and self.dimensions[1] is not None:
            self.svg_surface.set_width(self.dimensions[0], False)
            self.svg_surface.set_height(self.dimensions[1], False)
        elif self.dimensions[0] is not None:
            self.svg_surface.set_width(self.dimensions[0])
        elif self.dimensions[1] is not None:
            self.svg_surface.set_height(self.dimensions[1])

        self.svg_surface.set_position(self.position[0], self.position[1])

        context = self.parent.get_map().get_context()
        surface = self.parent.get_map().get_surface()
        self.svg_surface.draw(context, surface)

        pass
