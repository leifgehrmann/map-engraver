import os
import subprocess
import tempfile
import uuid
from pathlib import Path
import re

import cairocffi as cairo
from pangocffi import Layout
import pangocairocffi

from map_engraver.canvas.canvas_unit import CanvasUnit


class AutotraceText:
    scale = 10

    svg_path_d_regex = re.compile(
        r" d=\"(.*)\"",
        re.IGNORECASE
    )
    path_commands_regex = re.compile(
        r"((?P<command>[a-z])(?P<arguments>(\s*-?\d+\.?[\d]*\s*)*))",
        re.IGNORECASE
    )

    @staticmethod
    def convert_pango_layout_to_svg_draw_commands(layout: Layout) -> str:
        temp_dir = Path(tempfile.gettempdir())
        filename_input = temp_dir.joinpath(str(uuid.uuid1()) + '.png')
        filename_output = temp_dir.joinpath(str(uuid.uuid1()) + '.svg')

        layout_width = CanvasUnit.from_pango(layout.get_extents()[0].width)
        layout_height = CanvasUnit.from_pango(layout.get_extents()[0].height)
        surface_width_px = int(layout_width.px * AutotraceText.scale)
        surface_height_px = int(layout_height.px * AutotraceText.scale)

        # Create a cairo canvas and render the Pango Layout
        surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32,
            surface_width_px,
            surface_height_px
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
        try:
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
        except subprocess.CalledProcessError:
            # If this error happens, it's likely the program autotrace is not
            # installed.
            raise RuntimeError('Failed to run autotrace')

        os.remove(filename_input)

        try:
            with open(filename_output.as_posix()) as file:
                matches = re.findall(
                    AutotraceText.svg_path_d_regex,
                    file.read()
                )
                # Todo: Catch edge cases where there is more than one match.
                commands = matches[0]
        finally:
            os.remove(filename_output)

        # We do not expect autotrace to return strings with commas, but just in
        # case it does, we make an assertion here.
        assert ',' not in commands

        # We do not expect autotrace to return arc paths. If it does, the code
        # should be updated to handle them separately. This is because – unlike
        # the other path commands – not all the arguments can be scaled. For
        # example: In `A (rx ry angle large-arc-flag sweep-flag x y)+`, the
        # `angle`, `large-arc-flag`, and `sweep-flag` arguments should not be
        # scaled, whereas the other arguments can as they are coordinates.
        assert 'a' not in commands
        assert 'A' not in commands

        def replace_non_arc_commands(match):
            args_list = map(
                lambda x: str(float(x) / AutotraceText.scale),
                match.group('arguments').split(' ')
            )
            return match.group('command') + ' '.join(args_list)

        commands = re.sub(
            AutotraceText.path_commands_regex,
            replace_non_arc_commands,
            commands
        )

        return commands
