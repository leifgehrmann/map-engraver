from typing import Dict, Tuple

from map.features import Margins
from map.layer.ilayer import ILayer


class MarginLayer:
    parent = None
    margin_dimensions = [0, 0, 0, 0]
    legend_dimensions = [0, 0, 0, 0]
    interior_stroke_width = 1
    exterior_stroke_width = 1

    @staticmethod
    def create_from_dict(data: Dict, parent: 'ILayer') -> 'MarginLayer':
        layer = MarginLayer().set_parent(parent)
        if 'margin dimensions' in data:
            layer.set_margin_dimensions(data['margin dimensions'])
        if 'legend dimensions' in data:
            layer.set_legend_dimensions(data['legend dimensions'])
        if 'exterior stroke width' in data:
            layer.set_exterior_stroke_width(data['exterior stroke width'])
        if 'interior stroke width' in data:
            layer.set_interior_stroke_width(data['interior stroke width'])
        return layer

    def set_parent(self, parent: 'ILayer') -> 'MarginLayer':
        self.parent = parent
        return self

    def set_margin_dimensions(
            self,
            dimensions: Tuple[float, float, float, float]
    ) -> 'MarginLayer':
        self.margin_dimensions = dimensions
        return self

    def set_legend_dimensions(
            self,
            legend_dimensions: Tuple[float, float, float, float]
    ) -> 'MarginLayer':
        self.legend_dimensions = legend_dimensions
        return self

    def set_exterior_stroke_width(self, width: float) -> 'MarginLayer':
        self.exterior_stroke_width = width
        return self

    def set_interior_stroke_width(self, width: float) -> 'MarginLayer':
        self.interior_stroke_width = width
        return self

    def draw(self):
        canvas = self.parent.get_map().get_map_config().get_canvas_unit_dimensions()
        margins = self.margin_dimensions
        legend = self.legend_dimensions

        Margins() \
            .set_canvas_size(canvas[0], canvas[1]) \
            .set_margin(margins[0], margins[1], margins[2], margins[3]) \
            .set_legend(legend[0], legend[1], legend[2], legend[3]) \
            .set_exterior_stroke_width(self.exterior_stroke_width) \
            .set_interior_stroke_width(self.exterior_stroke_width) \
            .draw(self.parent.get_map().get_context())
