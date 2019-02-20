import logging
import os
import shutil

from flask import Flask, render_template
from PIL import Image, ImageDraw, ImageColor

app = Flask(__name__)

KEY_IMAGE_DIR = "static/images"


@app.route("/")
@app.route("/filename/<filename>")
def count(filename="./nyan.png"):
    logging.info('filename: %s', filename)
    im = Image.open(filename)
    counts = count_and_mark(im)
    total = sum([count for count in counts.values()])
    return render_template("count.html", color_count=counts, total=total, out_filename='out.png')


def count_and_mark(im):
    logging.info('Format: %s \tSize: %s', im.format, im.size)
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
        logging.info("%s) %s: %s", i, key, meth)
        result[key] = meth
    return result


def mark_image(im, color_count, scale=20, out_filename="out.png"):
    # Resize to im2
    w_ = im.size[0]
    h_ = im.size[1]
    im2 = im.resize((im.size[0] * scale, im.size[1] * scale), Image.NEAREST)

    method_map = get_draw_method_map(color_count)

    # Create key
    shutil.rmtree(KEY_IMAGE_DIR)
    os.mkdir(KEY_IMAGE_DIR)
    for key, method in method_map.items():
        logging.info('Creating key for (%s, %s)', key, method)
        hex_str = '#{}'.format(key)
        key_img = Image.new('RGB', (scale, scale), color=hex_str)
        d = ImageDraw.Draw(key_img)
        r, g, b = ImageColor.getrgb(hex_str)
        brightness = (r + g + b) / 3
        color = 'white'
        if brightness > (255 / 2):
            color = 'black'
        method(d, (0, 0), scale, color)
        key_img.save('static/{}.png'.format(key))

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
            fn = method_map.get(hex_key)
            fn(d, cursor, scale, color)
            cursor = (cursor[0] + scale, cursor[1])
        cursor = (0, cursor[1] + scale)

    # Draw grid
    d = ImageDraw.Draw(im2)
    grid_highlight_interval = 10
    primary, highlight = 'black', 'blue'
    for x in range(w_):
        color = highlight if x % grid_highlight_interval == 0 else primary
        c = x * scale
        d.line([(c, 0), (c, im2.size[0])], fill=color)
    for y in range(h_):
        color = highlight if y % grid_highlight_interval == 0 else primary
        c = y * scale
        d.line([(0, c), (im2.size[1], c)], fill=color)

    im2.save('static/' + out_filename)


#############################################
# Shape draw-ers.
#

def draw_blank(d, origin, scale, color):
    pass


def draw_ellipse(d, origin, scale, color):
    shrink = scale / 4
    e_origin = (origin[0] + shrink, origin[1] + shrink)
    e_opposite = (origin[0] + scale - shrink, origin[1] + scale - shrink)
    d.ellipse([e_origin, e_opposite], outline=color)


def draw_dot(d, origin, scale, color):
    size = scale / 10
    centre = (origin[0] + scale / 2, origin[1] + scale / 2)
    d.ellipse([(centre[0] - size / 2, centre[1] - size / 2),
               (centre[0] + size / 2, centre[1] + size / 2)],
              outline=color)


def draw_three_dots(d, origin, scale, color):
    shrink = scale / 3
    width = height = scale - (2 * shrink)
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


def draw_square(d, origin, scale, color):
    shrink = scale / 5
    s_origin = (origin[0] + shrink, origin[1] + shrink)
    s_opposite = (origin[0] + scale - shrink, origin[1] + scale - shrink)
    d.rectangle([s_origin, s_opposite], outline=color)


def draw_line(d, origin, scale, color):
    shrink = scale / 4
    s_origin = (origin[0] + shrink, origin[1] + shrink)
    s_opposite = (origin[0] + scale - shrink, origin[1] + scale - shrink)
    d.line([s_origin, s_opposite], fill=color)


def draw_triangle(d, origin, scale, color):
    shrink = scale / 4
    width = height = scale - (2 * shrink)
    t_origin = (origin[0] + shrink, origin[1] + shrink)
    top_pt = (t_origin[0] + width / 2, t_origin[1])
    left_pt = (t_origin[0], t_origin[1] + height)
    right_pt = (t_origin[0] + width, t_origin[1] + height)
    d.line([top_pt, left_pt, right_pt, top_pt], fill=color)


if __name__ == "__main__":
    debug = False
    ip, port = '127.0.0.1', 3000
    if os.environ.get('ENV') == 'c9':
        ip, port = '0.0.0.0', 8080
        debug = True
    logging.info("Running on IP %s and port %s", ip, port)
    app.run(ip, port, debug=debug)
