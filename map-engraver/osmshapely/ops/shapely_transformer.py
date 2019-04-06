from typing import Callable, Tuple, Optional, List, Union
from shapely.ops import transform

from typing import TypeVar

T = TypeVar('T')


class ShapelyTransformer:
    """
    Transforms shapely objects from one CRS to another.
    """

    def __init__(
            self,
            func: Optional[
                Callable[
                    [float, float, Optional[float]],
                    Union[Tuple[float, float], Tuple[float, float, float]]
                ]
            ] = None
    ):
        self.func = func

    def transform(self, geom: T) -> T:
        """
        :param geom:
            the geometry object to transform
        :return:
            the transformed geometry object
        """
        if self.func is None:
            return geom
        return transform(self.func, geom)

    def transform_list(self, geoms: List[T]) -> List[T]:
        """
        :param geoms:
            geometry objects to transform
        :return:
            the transformed geometry objects
        """
        return [self.transform(geom) for geom in geoms]
