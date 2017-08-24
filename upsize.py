from PIL import Image, ImageDraw

DRAW_FNS = [
	ImageDraw.Draw.ellipse
]

def construct_draw_map(im, color_list):
	# Map each color to a method that knows how to draw a shape
	print '# of colors: ' % len(color_list)
	draw_map = {}
	for i, color in enumerate(color_list):
		print '%s: %s' % (i, color)
		method = DRAW_FNS[len(DRAW_FNS%i)]
		draw_map[color] = method
	return 



def draw_marks(im, factor=10, save_filename='out.png'):
	w_ = im.size[0]
	h_ = im.size[1]
	im2 = im.resize((im.size[0]*factor, im.size[1]*factor), Image.NEAREST)
	# image is now factor * w_h wide, with w_h "pixels" (cells)
	# Each cell is `factor` wide.
	# Eventually, map original colors of pixels to a series of shapes,

	cursor = (0, 0)

	for y in range(h_):
		for x in range(w_):
			draw(im2, cursor[0], cursor[1], factor)
			cursor = (cursor[0] + factor, cursor[1])
		cursor = (0, cursor[1] + factor)

	return im2

def draw(im, x, y, factor, method=None):
	d = ImageDraw.Draw(im)
	d.ellipse((x, y, x+factor, y+factor))