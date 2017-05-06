import json
import os
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

	im2.save(save_filename)
	return im2


if __name__ == "__main__":
	ip, port = '127.0.0.1', 3000
	if os.environ.get('ENV') == 'c9':
		ip, port = '0.0.0.0', 8080
	app.run(ip, port)