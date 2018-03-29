from typing import Dict, Tuple

from map.features import Margins
from map.layer.ilayer import ILayer


class MarginLayer:
    parent = None
    margin_dimensions = [0, 0, 0, 0]
    legend_dimensions = [0, 0, 0, 0]

    @staticmethod
    def create_from_dict(data: Dict, parent: 'ILayer') -> 'MarginLayer':
        layer = MarginLayer().set_parent(parent)
        if 'margin' in data:
            layer.set_margin_dimensions(data['margin'])
        if 'legend' in data:
            layer.set_legend_dimensions(data['legend'])
        return layer

    def set_parent(self, parent: 'ILayer') -> 'MarginLayer':
        self.parent = parent
        return self

    def set_margin_dimensions(self, dimensions: Tuple[float, float, float, float]) -> 'MarginLayer':
        self.margin_dimensions = dimensions
        return self

    def set_legend_dimensions(self, legend_dimensions: Tuple[float, float, float, float]) -> 'MarginLayer':
        self.legend_dimensions = legend_dimensions
        return self

    def draw(self):
        canvas = self.parent.get_map().get_map_config().get_dimensions()
        margins = self.margin_dimensions
        legend = self.legend_dimensions

        Margins() \
            .set_canvas_size(canvas[0], canvas[1]) \
            .set_margin(margins[0], margins[1], margins[2], margins[3]) \
            .set_legend(legend[0], legend[1], legend[2], legend[3]) \
            .draw(self.parent.get_map().get_context())
