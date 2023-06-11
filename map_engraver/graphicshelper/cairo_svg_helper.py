from cairosvg.path import path
from cairocffi import Context


class CairoSvgHelper:
    @staticmethod
    def execute_svg_path_in_cairo(ctx: Context, d: str):

        class FauxSurface(object):
            context = ctx

        class FauxNode(object):
            def get(self, *args) -> str:
                return d

        path(FauxSurface(), FauxNode())
