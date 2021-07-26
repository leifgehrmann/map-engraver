import abc

from map_engraver.canvas import Canvas


class Drawable(abc.ABC):
    @abc.abstractmethod
    def draw(self, canvas: Canvas):
        pass
