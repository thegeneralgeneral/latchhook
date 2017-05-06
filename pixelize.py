from PIL import Image, ImageEnhance

image = Image.open('../280.png')


def pixelize(im,
             contrast_factor=2,
             brightness_factor=1.2,
             colors=5,
             output_size=(64, 64),
             output_filename='output'):

    brightener = ImageEnhance.Brightness(im)
    im2 = brightener.enhance(brightness_factor)

    contraster = ImageEnhance.Contrast(im2)  # contrast on im2
    im2 = contraster.enhance(contrast_factor)

    im2 = im2.convert('P', palette=Image.ADAPTIVE, colors=colors)
    im2 = im2.resize(output_size)
    output_filename = '{name}_{brightness}_{contrast}_{colors}'.format(
        name=output_filename,
        brightness=brightness_factor,
        contrast=contrast_factor,
        colors=colors
    ).replace('.', '')
    im2.save('%s.png' % output_filename)

pixelize(image)
