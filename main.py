import json
import os
import sys
import logging

from PIL import Image, ImageDraw
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
@app.route("/<filename>")
def count(filename="../nyan_pattern_pixel.png"):
	logging.info('filename: %s', filename)
	counts = get_counts(filename)
	total = sum([count for count in counts.values()])
	return render_template("count.html", color_count=counts, total=total)

def get_counts(filename):
	im = Image.open(filename)

	print 'Format: %s \tSize: %s', (im.format, im.size)
	im = im.convert('RGB')

	color_count = {}

	print 'total pixels: %s' % (im.size[0]*im.size[1])

	for x in range(0, im.size[0]):
		for y in range(0, im.size[1]):
			r, g, b = im.getpixel((x, y))
			hex_value = '#{:02x}{:02x}{:02x}'.format(r, g, b)
			prev_count = color_count.get(hex_value, 0)
			color_count[hex_value] = prev_count + 1

	sordid = sorted(color_count.iteritems())
	print sordid
	for key, count in sordid:
		print '%s\t\t%s' % (key, count)

	return color_count

def draw_marks(im, factor=10, save_filename='out.png'):
	w_ = im.size[0]
	h_ = im.size[1]
	im2 = im.resize((im.size[0]*factor, im.size[1]*factor), Image.NEAREST)
	# image is now factor * w_h wide, with w_h "pixels" (cells)
	# Each cell is `factor` wide.
	# Eventually, map original colors of pixels to a series of shapes,


	# Draw a circle in the first cell.
	cursor = (0, 0)
	centre = (cursor[0]+factor, cursor[1] + factor)

	draw = ImageDraw.Draw(im2)
	draw.ellipse(cursor[0], cursor[1], centre[0], centre[1])

	im2.save(save_filename)
	return im2


if __name__ == "__main__":
	ip, port = '127.0.0.1', 3000
	if os.environ.get('ENV') == 'c9':
		ip, port = '0.0.0.0', 8080
	app.run(ip, port)