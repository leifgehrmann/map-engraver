from typing import Callable, Tuple
import cairocffi as cairo

from map import MapConfig
import osmparser


class IMap:
    """Interface Map to allow type hinting"""

    def get_surface(self) -> cairo.Surface:
        pass

    def get_context(self) -> cairo.Context:
        pass

    def get_map_config(self) -> MapConfig:
        pass

    def get_map_data(self) -> osmparser.Map:
        pass

    def get_map_projection_function(self) -> Callable[[Tuple[float, float]], Tuple[float, float]]:
        pass

    def draw(self):
        pass
