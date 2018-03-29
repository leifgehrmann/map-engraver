from cairosvg.helpers import (node_format)
from cairosvg import parser as parser
from cairocffi import Context, Surface
from cairocffi import Matrix
from graphicshelper.cario_svg_surface_fork import Surface as CairoSVGSurface


class SvgSurface:
    def __init__(self, filename):
        self.filename = filename
        self.position_x = 0
        self.position_y = 0
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
        self.svg_width, self.svg_height, _ = node_format(self, tree)

    def set_position(self, x=0, y=0):
        self.position_x = x
        self.position_y = y

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
        ctx.translate(self.position_x, self.position_y)
        ctx.scale(self.width / self.svg_width, self.height / self.svg_height)
        CairoSVGSurface(self.tree, surface, ctx, 96)
        ctx.restore()
