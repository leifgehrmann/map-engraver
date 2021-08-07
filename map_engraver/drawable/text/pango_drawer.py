import pangocairocffi
import pangocffi

from map_engraver.canvas import Canvas
from map_engraver.drawable.drawable import Drawable


class PangoDrawer(Drawable):
    def draw(self, canvas: Canvas):
        canvas.context.set_source_rgba(0, 0, 0, 1)
        width = canvas.width / canvas.scale
        height = canvas.height / canvas.scale
        layout = pangocairocffi.create_layout(canvas.context)
        layout.set_width(pangocffi.units_from_double(width))
        layout.set_height(pangocffi.units_from_double(height))
        layout.set_alignment(pangocffi.Alignment.CENTER)
        layout.set_markup('<span font="italic 16">Hi from Παν語</span>')

        # Render the layout
        pangocairocffi.show_layout(canvas.context, layout)
