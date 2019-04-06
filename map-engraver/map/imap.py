from typing import Callable, Tuple, Optional, Union
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

    def get_map_projection_function(self) -> Callable[
        [float, float, Optional[float]],
        Union[Tuple[float, float], Tuple[float, float, float]]
    ]:
        pass

    def draw(self):
        pass
