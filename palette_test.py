import sys
from PIL import Image
from palette import *
from util import *

def palette_argument_test(image):
    tests = []
    for random_init, black in itertools.product([True, False], repeat=2):
        print('random_init: {}, black: {}'.format(random_init, black))
        colors = build_palette(image, random_init=random_init, black=black)
        tests.append(draw_palette(colors))

    return v_merge(tests)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        image_name = sys.argv[1]
    else:
        image_name = 'input.jpg'

    image = Image.open(image_name)
    print(image_name, image.format, image.size, image.mode)
    lab = rgb2lab(image)

    #build palette
    palette = build_palette(lab)
    palette_image = draw_palette(palette)
    palette_image.save('palette.jpg')

    #argument test
    palette_arg_test = palette_argument_test(lab)
    palette_arg_test.save('palette_test.jpg')
