import sys
from PIL import Image
from palette import *
from util import *

if __name__ == '__main__':
    if len(sys.argv) > 1:
        image_name = sys.argv[1]
    else:
        image_name = 'input.jpg'

    image = Image.open(image_name)
    print(image_name, image.format, image.size, image.mode)

    lab = rgb2lab(image)
    palette_test(lab).show()