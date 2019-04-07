from typing import Dict

from map.features import Background as BackgroundDrawer
from map.layer.ilayer import ILayer


class BackgroundLayer:
    parent = None
    color = None

    @staticmethod
    def create_from_dict(data: Dict, parent: 'ILayer') -> 'BackgroundLayer':
        layer = BackgroundLayer().set_parent(parent)
        if 'color' in data:
            layer.fill_color = data['color']
        return layer

    def set_parent(self, parent: 'ILayer') -> 'BackgroundLayer':
        self.parent = parent
        return self

    def draw(self):
        canvas = self.parent.get_map().get_map_config()\
            .get_canvas_unit_dimensions()

        drawer = BackgroundDrawer()
        drawer.set_canvas_size(canvas[0], canvas[1])
        if self.color is not None:
            drawer.set_color(*self.color)
        drawer.draw(self.parent.get_map().get_context())
