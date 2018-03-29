import math

import cairocffi as cairo
from shapely.geometry import LineString

from map.features import Text

surface = cairo.PDFSurface("../data/output/draw_text.pdf", 40, 60)
ctx = cairo.Context(surface)


def draw_label(text, x, y):
    original = ctx.get_matrix()
    original_font = ctx.get_font_face()
    ctx.translate(x, y)
    font = cairo.ToyFontFace('', weight=1)
    ctx.set_source_rgba(0,0,0,1)
    ctx.set_font_face(font)
    ctx.scale(1 / 15)  # Default font size is 10 mm (1cm)
    ctx.show_text(text)
    ctx.fill()
    ctx.set_font_face(original_font)
    ctx.set_matrix(original)


sin_wave = []
for x in range(0,55):
    sin_wave.append([x/4 + 1, math.sin(x/8) * 2 + 4])
line_string_sine = LineString(sin_wave)
line_string_straight = LineString([[1, 9], [12, 9]])

draw_label("Basic Test", 1, 1)
Text("HELLO WORLD", line_string_sine).draw(ctx)
Text("HELLO WORLD", line_string_straight).draw(ctx)

draw_label("Position Trimming", 16, 1)
for x in range(0,10):
    line_string = LineString([[17, x + 2], [27 - x, x + 2]])
    Text("HELLO WORLD", line_string).set_text_height(0.5).draw(ctx)
    line_string = LineString([[29, x + 2], [29 - x - 1, x + 2]])
    Text("HELLO WORLD", line_string).set_text_height(0.5).draw(ctx)

draw_label("Text Alignment", 30, 1)
alignment_options = ['left', 'center', 'right']
for alignment_option_index in range(len(alignment_options)):
    alignment_option = alignment_options[alignment_option_index]
    line_string_upright = LineString([[31, 2 + alignment_option_index * 2], [38, 2 + alignment_option_index * 2]])
    line_string_inverse = LineString([[38, 3 + alignment_option_index * 2], [31, 3 + alignment_option_index * 2]])
    Text(alignment_option, line_string_upright) \
        .set_text_alignment(alignment_option) \
        .set_text_height(0.5) \
        .draw(ctx)
    Text(alignment_option, line_string_inverse) \
        .set_text_alignment(alignment_option) \
        .set_text_height(0.5) \
        .draw(ctx)

draw_label("Text Height", 16, 14)
for x in range(0,10 + 1):
    line_string = LineString([[17 + x * 2, 16], [19 + x * 2 - 0.5, 16]])
    Text("ABC", line_string).set_line_text_offset((5 - x) * 0.1).set_text_height(0.5).draw(ctx)
    line_string = LineString([[19 + x * 2 - 0.5, 18], [17 + x * 2, 18]])
    Text("ABC", line_string).set_line_text_offset((5 - x) * 0.1).set_text_height(0.5).draw(ctx)

draw_label("Upright Text", 1, 13)
draw_label("Upright Text Inverted", 1, 29)
for x in range(0,16):
    angle = x / 16 * math.pi * 2
    center_x = 8
    center_y = 20
    line_string = LineString([
        [center_x + math.cos(angle) * 2, center_y + math.sin(angle) * 2],
        [center_x + math.cos(angle) * 6, center_y + math.sin(angle) * 6]
    ])
    Text("ABC efg |_^", line_string).set_text_height(0.5).draw(ctx)

    line_string = LineString(reversed([
        [center_x + math.cos(angle) * 2, center_y + 16 + math.sin(angle) * 2],
        [center_x + math.cos(angle) * 6, center_y + 16 + math.sin(angle) * 6]
    ]))
    Text("ABC efg |_^", line_string).set_text_height(0.5).draw(ctx)


draw_label("Upright Text With Line Offset + Inverted", 16, 21)
for x in range(0,16):
    angle = x / 16 * math.pi * 2

    center_x = 20
    center_y = 28

    line_string = LineString([
        [center_x + math.cos(angle) * 2, center_y + math.sin(angle) * 2],
        [center_x + math.cos(angle) * 6, center_y + math.sin(angle) * 6]
    ])
    Text("ABC efg |_^", line_string).set_line_text_offset(0.5).set_text_height(0.5).draw(ctx)

    line_string = LineString(reversed([
        [center_x + 13 + math.cos(angle) * 2, center_y + math.sin(angle) * 2],
        [center_x + 13 + math.cos(angle) * 6, center_y + math.sin(angle) * 6]
    ]))
    Text("ABC efg |_^", line_string).set_line_text_offset(0.5).set_text_height(0.5).draw(ctx)

draw_label("Upright Text With Concentric Paths + Inverted", 16, 36)
for x in range(0,5):
    angle = x / 7 * math.pi * 2

    center_x = 20
    center_y = 42

    circle = []
    for a in range(0, 200 + 1):
        circle.append([
            center_x + math.cos(angle + a / 200 * math.pi * 2) * (x+1),
            center_y + math.sin(angle + a / 200 * math.pi * 2) * (x+1)
        ])

    line_string = LineString(circle)
    circle_text = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    circle_text += "-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    circle_text += "-abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    Text(circle_text, line_string)\
        .set_text_height(0.5)\
        .draw(ctx)

    circle = []
    for a in range(0, 200 + 1):
        circle.append([
            center_x + 13 + math.cos(angle + a / 200 * math.pi * 2) * (x + 1),
            center_y + math.sin(angle + a / 200 * math.pi * 2) * (x + 1)
        ])

    line_string = LineString(reversed(circle))
    Text(circle_text, line_string) \
        .set_text_height(0.5) \
        .draw(ctx)

surface.flush()
surface.finish()