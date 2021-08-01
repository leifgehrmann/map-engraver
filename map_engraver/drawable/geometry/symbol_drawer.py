import abc
from typing import List, Union

from shapely.geometry import Point

from map_engraver.canvas import Canvas
from map_engraver.drawable.drawable import Drawable
from functools import cmp_to_key


class SymbolDrawer(Drawable, abc.ABC):
    points: List[Union[Point]]

    def __init__(self):
        self.points = []
        self.z_sort_func = SymbolDrawer.default_z_sort_func

    def draw(self, canvas: Canvas):
        self.points = self.z_sort_func(self.points)
        for point in self.points:
            self.draw_symbol(point, canvas)

    @abc.abstractmethod
    def draw_symbol(self, point: Point, canvas: Canvas):
        pass

    @staticmethod
    def default_z_sort_func(points: List[Point]) -> List[Point]:
        """
        Sorts the rendering of symbols on the canvas based on how far down the
        canvas the point will appear.
        """
        def func(a: Point, b: Point) -> int:
            if a.y < b.y:
                return -1
            if a.y > b.y:
                return 1
            return int(a.x - b.x)

        return sorted(points, key=cmp_to_key(func))
