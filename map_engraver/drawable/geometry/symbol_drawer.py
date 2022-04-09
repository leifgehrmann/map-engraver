import abc
from typing import List, Union, Dict, Iterable, TypeVar, Tuple

from shapely.geometry import Point

from map_engraver.canvas import Canvas
from map_engraver.drawable.drawable import Drawable
from functools import cmp_to_key

T = TypeVar('T')


class SymbolDrawer(Drawable, abc.ABC):
    points: Union[Dict[T, Point], Iterable[Point]]

    def __init__(self):
        self.points = []
        self.z_sort_func = SymbolDrawer.default_z_sort_func

    def draw(self, canvas: Canvas):
        dict_points: Dict[T, Point]
        if not isinstance(self.points, dict):
            dict_points = dict((i, j) for i, j in enumerate(self.points))
        else:
            dict_points = self.points

        points = self.z_sort_func(dict_points)
        for key, point in points:
            self.draw_symbol(key, point, canvas)

    @abc.abstractmethod
    def draw_symbol(self, idx: T, point: Point, canvas: Canvas):
        pass

    @staticmethod
    def default_z_sort_func(points: Dict[T, Point]) -> List[Tuple[T, Point]]:
        """
        Sorts the rendering of symbols on the canvas based on how far down the
        canvas the point will appear.
        """
        def func(a: Tuple[T, Point], b: Tuple[T, Point]) -> int:
            if a[1].y < b[1].y:
                return -1
            if a[1].y > b[1].y:
                return 1
            return int(a[1].x - b[1].x)

        return sorted(points.items(), key=cmp_to_key(func))
