from cairocffi import Context
from typing import List, Union, Callable, no_type_check
from osmshapely import LineString
from ..text import Text
from ..utilities import ProgressController


class LabelDrawer(ProgressController):

    failed_to_render_callable = None

    def set_failed_to_render_callable(
            self,
            func: Callable[[LineString], no_type_check]
    ) -> 'LabelDrawer':
        self.failed_to_render_callable = func
        return self

    def draw_labels(self, ctx: Context, highways: List[LineString]):
        # font = cairo.ToyFontFace('CMU Concrete', weight=1)
        # ctx.set_font_face(font)
        ctx.set_source_rgba(0, 0, 0, 1)
        self._draw_iterator(ctx, highways, self._draw_label)

    def _draw_iterator(
            self,
            ctx: Context,
            line_strings: List[Union[LineString]],
            render_function: Callable[
                [Context, Union[LineString]],
                no_type_check
            ]
    ):
        total = len(line_strings)
        for line_string in line_strings:
            render_function(ctx, line_string)
            if self.progress_callable is not None:
                self.progress_callable(render_function.__name__, 1, total)

    def _draw_label(self, ctx: Context, line_string: Union[LineString]):

        if not isinstance(line_string, LineString):
            pass

        tags = line_string.get_osm_tags()
        if 'name' in tags:
            text = Text(tags['name'].upper(), line_string)
            text.set_text_height(0.5)
            try:
                text.draw(ctx)
            except NotImplementedError:
                if self.failed_to_render_callable is not None:
                    self.failed_to_render_callable(line_string)
                # Todo: fix text to not throw NotImplementedError
                pass
