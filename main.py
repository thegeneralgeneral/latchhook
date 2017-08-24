import json
import sys
import logging

from PIL import Image, ImageDraw, ImageColor
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
@app.route("/filename/<filename>")
def count(filename="../nyan_pattern_pixel.png"):
    logging.info('filename: %s', filename)
    counts = count_and_mark(filename)
    # counts = get_counts(filename)
    total = sum([count for count in counts.values()])
    return render_template("count.html", color_count=counts, total=total)


def count_and_mark(filename):
    im = Image.open(filename)
    print 'Format: %s \tSize: %s', (im.format, im.size)
    im = im.convert('RGB')

    color_count = get_counts(im)

    mark_image(im, color_count)

    return color_count


def get_counts(im):
    color_count = {}

    for x in range(0, im.size[0]):
        for y in range(0, im.size[1]):
            r, g, b = im.getpixel((x, y))
            hex_value = '{:02x}{:02x}{:02x}'.format(r, g, b)
            prev_count = color_count.get(hex_value, 0)
            color_count[hex_value] = prev_count + 1

    return color_count


def get_draw_method_map(color_count):
    methods = [
        draw_blank,
        draw_dot,
        draw_line,
        draw_three_dots,
        draw_triangle,
        draw_ellipse,
        draw_square
    ]
    result = {}

    sorted_color_keys = sorted(color_count.keys())
    sorted_color_keys.reverse()
    for i, key in enumerate(sorted_color_keys):
        meth = methods[i % len(methods)]
        print "%s) %s: %s" % (i, key, meth)
        result[key] = meth
    return result


def mark_image(im, color_count, factor=20, out_filename="out.png"):
    # Resize to im2
    w_ = im.size[0]
    h_ = im.size[1]
    im2 = im.resize((im.size[0] * factor, im.size[1] * factor), Image.NEAREST)

    method_map = get_draw_method_map(color_count)

    # Create key

    for key, method in method_map.iteritems():
        f = factor
        hex_str = '#{}'.format(key)
        print hex_str
        key_img = Image.new('RGB', (f, f), color=hex_str)
        d = ImageDraw.Draw(key_img)
        r, g, b = ImageColor.getrgb(hex_str)
        brightness = (r + g + b) / 3
        color = 'white'
        if brightness > (255 / 2):
            color = 'black'
        method(d, (0, 0), f, color)
        key_img.save('static/%s.png' % key)

    # Draw markers
    d = ImageDraw.Draw(im2)
    cursor = (0, 0)
    for y in range(h_):
        for x in range(w_):
            r, g, b = im.getpixel((x, y))
            brightness = (r + g + b) / 3
            color = 'white'
            if brightness > (255 / 2):
                color = 'black'
            hex_key = '{:02x}{:02x}{:02x}'.format(r, g, b)
            fn = method_map.get(hex_key)  # get method by hex string (gross)
            # print '%s => %s' % (hex_key, fn)
            fn(d, cursor, factor, color)
            cursor = (cursor[0] + factor, cursor[1])
        cursor = (0, cursor[1] + factor)

    # Draw grid
    d = ImageDraw.Draw(im2)
    grid_highlight_interval = 10
    primary, highlight = 'black', 'blue'
    for x in range(w_):
        color = highlight if x % grid_highlight_interval == 0 else primary
        c = x * factor
        d.line([(c, 0), (c, im2.size[0])], fill=color)
    for y in range(h_):
        color = highlight if y % grid_highlight_interval == 0 else primary
        c = y * factor
        d.line([(0, c), (im2.size[1], c)], fill=color)

    im2.save('static/' + out_filename)


#############################################
# Shape draw-ers.
#

def draw_blank(d, origin, factor, color):
    pass


def draw_ellipse(d, origin, factor, color):
    shrink = factor / 4
    e_origin = (origin[0] + shrink, origin[1] + shrink)
    e_opposite = (origin[0] + factor - shrink, origin[1] + factor - shrink)
    d.ellipse([e_origin, e_opposite], outline=color)


def draw_dot(d, origin, factor, color):
    size = factor / 10
    centre = (origin[0] + factor / 2, origin[1] + factor / 2)
    d.ellipse([(centre[0] - size / 2, centre[1] - size / 2),
               (centre[0] + size / 2, centre[1] + size / 2)],
              outline=color)


def draw_three_dots(d, origin, factor, color):
    shrink = factor / 3
    width = height = factor - (2 * shrink)
    t_origin = (origin[0] + shrink, origin[1] + shrink)
    top_pt = (t_origin[0] + width / 2, t_origin[1])
    left_pt = (t_origin[0], t_origin[1] + height)
    right_pt = (t_origin[0] + width, t_origin[1] + height)

    def draw_one_dot(d, radius, point, color):
        d.ellipse([(point[0] - radius, point[1] - radius),
                   (point[0] + radius, point[1] + radius)],
                  outline=color)

    for pt in [top_pt, left_pt, right_pt]:
        draw_one_dot(d, 1, pt, color)


def draw_square(d, origin, factor, color):
    shrink = factor / 5
    s_origin = (origin[0] + shrink, origin[1] + shrink)
    s_opposite = (origin[0] + factor - shrink, origin[1] + factor - shrink)
    d.rectangle([s_origin, s_opposite], outline=color)


def draw_line(d, origin, factor, color):
    shrink = factor / 4
    s_origin = (origin[0] + shrink, origin[1] + shrink)
    s_opposite = (origin[0] + factor - shrink, origin[1] + factor - shrink)
    d.line([s_origin, s_opposite], fill=color)


def draw_triangle(d, origin, factor, color):
    shrink = factor / 4
    width = height = factor - (2 * shrink)
    t_origin = (origin[0] + shrink, origin[1] + shrink)
    top_pt = (t_origin[0] + width / 2, t_origin[1])
    left_pt = (t_origin[0], t_origin[1] + height)
    right_pt = (t_origin[0] + width, t_origin[1] + height)
    d.line([top_pt, left_pt, right_pt, top_pt], fill=color)


def draw_diamond(d, origin, factor, color):
    shrink = factor / 4
    width = height = factor - (2 * shrink)
    t_origin = (origin[0] + shrink, origin[1] + shrink)
    top_pt = (t_origin[0] + width / 2, t_origin[1])
    left_pt = (t_origin[0], t_origin[1] + height)
    right_pt = (t_origin[0] + width, t_origin[1] + height)
    bottom_pt = ()
    d.line([top_pt, left_pt, right_pt, top_pt], fill=color)


if __name__ == "__main__":
    app.run(debug=True)
