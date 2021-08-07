from typing import Union, List

import pangocairocffi

from map_engraver.canvas import Canvas
from map_engraver.data.pango.layout import Layout
from map_engraver.drawable.drawable import Drawable


class PangoDrawer(Drawable):

    pango_objects: List[Union[Layout]]

    def __init__(self):
        self.objects = []

    def draw(self, canvas: Canvas):
        for pango_object in self.pango_objects:
            canvas.context.save()
            canvas.context.translate(*pango_object.position.pt)
            pangocairocffi.show_layout(
                canvas.context,
                pango_object.pango_layout
            )
            canvas.context.restore()
