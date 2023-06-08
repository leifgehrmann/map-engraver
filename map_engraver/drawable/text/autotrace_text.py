import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Optional

import cairocffi as cairo
from pangocffi import Layout
import pangocairocffi

from map_engraver.canvas.canvas_unit import CanvasUnit


class AutotraceText:
    scale = 5

    @staticmethod
    def reset_config():
        AutotraceText.scale = 5

    @staticmethod
    def convert_pango_layout_to_svg_draw_commands(layout: Layout) -> str:
        temp_dir = Path(tempfile.gettempdir())
        filename_input = temp_dir.joinpath(str(uuid.uuid1()) + '.png')
        filename_output = temp_dir.joinpath(str(uuid.uuid1()) + '.svg')

        # Create a cairo canvas and render the Pango Layout
        surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32,
            int(CanvasUnit.from_pango(layout.get_extents()[0].width).px * AutotraceText.scale),
            int(CanvasUnit.from_pango(layout.get_extents()[0].height).px * AutotraceText.scale)
        )
        context = cairo.Context(surface)
        context.scale(AutotraceText.scale)

        context.set_source_rgb(1, 1, 1)
        context.rectangle(0, 0, surface.get_width(), surface.get_height())
        context.fill()

        context.set_source_rgb(0, 0, 0)
        pangocairocffi.show_layout(
            context,
            layout
        )
        surface.write_to_png(filename_input.as_posix())
        surface.finish()

        # Run autotrace on bitmap and convert to SVG, via the command line
        subprocess.run([
            "autotrace " +
            "-centerline " +
            "-color-count 2 " +
            "-output-format svg " +
            "-corner-threshold 170 " +
            "-background-color FFFFFF " +
            filename_input.as_posix() + " " +
            "-output-file " + filename_output.as_posix()
            ],
            shell=True,
            check=True,
            # Todo: "SHELL" is the default shell for the user, not the current.
            #       Ideally we should find a way to get the current shell
            #       environment, as that is more likely where the autotrace
            #       command will be in the user's path.
            executable=os.environ.get('SHELL'),
            capture_output=True
        )

        # Todo: Read the SVG path
        os.remove(filename_input)
        os.remove(filename_output)

        return "Todo:"


