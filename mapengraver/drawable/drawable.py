import abc

from mapengraver.canvas import Canvas


class Drawable(abc.ABC):
    @abc.abstractmethod
    def draw(self, canvas: Canvas):
        pass
