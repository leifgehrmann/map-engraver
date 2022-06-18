from typing import Any

from cairosvg.helpers import (node_format)
from cairosvg import parser as parser
from cairocffi import Context, Surface
from .cario_svg_surface_fork import Surface as CairoSVGSurface
from ..canvas.canvas_unit import CanvasUnit


class SvgSurface:
    filename: str
    translate_x: float
    translate_y: float
    origin_x: float
    origin_y: float
    rotation: float
    svg_width: float
    svg_height: float
    width: float
    height: float
    tree: Any

    def __init__(self, filename):
        self.filename = filename
        self.translate_x = 0
        self.translate_y = 0
        self.origin_x = 0
        self.origin_y = 0
        self.rotation = 0
        self.svg_width = 0
        self.svg_height = 0
        self.width = 0
        self.height = 0
        self.tree = None

        with open(filename, 'r') as file:
            data = file.read()
            self.tree = parser.Tree(bytestring=data)
            self.read_dimensions_from_svg(self.tree)
            self.width = self.svg_width
            self.height = self.svg_height

    def read_dimensions_from_svg(self, tree):
        """
        :param tree:
        :return: Returns the size of the image in pixels. If the image is
                 measured in points, it will error.
        """
        svg_width_px, svg_height_px, _ = node_format(self, tree)
        self.svg_width = CanvasUnit.from_px(svg_width_px).pt
        self.svg_height = CanvasUnit.from_px(svg_height_px).pt

    def set_origin(self, x, y):
        self.origin_x = x
        self.origin_y = y

    def set_translation(self, x, y):
        self.translate_x = x
        self.translate_y = y

    def set_rotation(self, r):
        self.rotation = r

    def set_width(self, width, preserve_ratio=True):
        if preserve_ratio:
            self.height *= width / self.width
        self.width = width

    def set_height(self, height, preserve_ratio=True):
        if preserve_ratio:
            self.width *= height / self.height
        self.height = height

    def draw(self, ctx: Context, surface: Surface):
        ctx.save()
        ctx.translate(
            self.translate_x,
            self.translate_y
        )
        ctx.rotate(self.rotation)
        ctx.scale(self.width / self.svg_width, self.height / self.svg_height)
        ctx.translate(-self.origin_x, -self.origin_y)
        CairoSVGSurface(
            self.tree, None, 96, output_cairo=surface, output_cairo_context=ctx
        )
        ctx.restore()
