from PIL import Image, ImageCms

def rgb2lab(image):
    RGB_p = ImageCms.createProfile('sRGB')
    LAB_p = ImageCms.createProfile('LAB')
    return ImageCms.profileToProfile(image, RGB_p, LAB_p, outputMode='LAB')

def lab2rgb(image):
    RGB_p = ImageCms.createProfile('sRGB')
    LAB_p = ImageCms.createProfile('LAB')
    return ImageCms.profileToProfile(image, LAB_p, RGB_p, outputMode='RGB')

def rgb2lab_slow(image):
    result = Image.new('LAB', image.size)
    result_pixels = result.load()
    for i in range(image.width):
        for j in range(image.height):
            result_pixels[i, j] = ByteLAB(RGBtoLAB(image.getpixel((i, j))[:3]))
    return result

def lab2rgb_slow(image):
    result = Image.new('RGB', image.size)
    result_pixels = result.load()
    for i in range(image.width):
        for j in range(image.height):
            result_pixels[i, j] = RegularRGB(LABtoRGB(RegularLAB(image.getpixel((i, j)))))
    return result

def LABtoXYZ(LAB):
    def f(n):
        return n**3 if n > 6/29 else 3 * ((6/29)**2) * (n - 4/29)

    assert(ValidLAB(LAB))

    L, a, b = LAB
    X = 95.047 * f((L+16)/116 + a/500)
    Y = 100.000 * f((L+16)/116)
    Z = 108.883 * f((L+16)/116  - b/200)
    return (X, Y, Z)

def XYZtoRGB(XYZ):
    def f(n):
        return n*12.92 if n <= 0.0031308 else (n**(1/2.4)) * 1.055 - 0.055

    X, Y, Z = [x/100 for x in XYZ]
    R = f(3.2406*X + -1.5372*Y + -0.4986*Z) * 255
    G = f(-0.9689*X + 1.8758*Y + 0.0415*Z) * 255
    B = f(0.0557*X + -0.2040*Y + 1.0570*Z) * 255
    return (R, G, B)

def LABtoRGB(LAB):
    return XYZtoRGB(LABtoXYZ(LAB))

def RGBtoXYZ(RGB):
    def f(n):
        return n/12.92 if n <= 0.04045 else ((n+0.055)/1.055)**2.4

    assert(ValidRGB(RGB))

    R, G, B = [f(x/255) for x in RGB]
    X = (0.4124*R + 0.3576*G + 0.1805*B) * 100
    Y = (0.2126*R + 0.7152*G + 0.0722*B) * 100
    Z = (0.0193*R + 0.1192*G + 0.9505*B) * 100
    return (X, Y, Z)

def XYZtoLAB(XYZ):
    def f(n):
        return n**(1/3) if n > (6/29)**3 else (n / (3*((6/29)**2))) + (4/29)

    X, Y, Z = XYZ
    X /= 95.047
    Y /= 100.000
    Z /= 108.883

    L = 116*f(Y) - 16
    a = 500 * (f(X) - f(Y))
    b = 200 * (f(Y) - f(Z))
    return (L, a, b)

def RGBtoLAB(RGB):
    return XYZtoLAB(RGBtoXYZ(RGB))

def ValidRGB(RGB):
    return False not in [0 <= x <= 255 for x in RGB]

def ValidLAB(LAB):
    L, a, b = LAB
    return 0 <= L <= 100 and -128 <= a <= 127 and -128 <= b <= 127

def RegularLAB(LAB):
    return (LAB[0] / 255 * 100, LAB[1] - 128, LAB[2] - 128)

def ByteLAB(LAB):
    return (int(LAB[0] / 100 * 255), int(LAB[1] + 128), int(LAB[2] + 128))

def RegularRGB(RGB):
    return tuple([int(max(0, min(x, 255))) for x in RGB])

def distance(color_a, color_b):
    return (sum([(a-b)**2 for a, b in zip(color_a, color_b)]))**0.5

def compare(image_a, image_b):
    print('compare', list(image_a.getdata()) == list(image_b.getdata()))

def h_merge(images):
    width = sum([image.width for image in images])
    height = max([image.height for image in images])

    merge = Image.new(images[0].mode, (width, height))
    offset = 0
    for image in images:
        merge.paste(image, (offset, 0))
        offset += image.width

    return merge

def v_merge(images):
    width = max([image.width for image in images])
    height = sum([image.height for image in images])

    merge = Image.new(images[0].mode, (width, height))
    offset = 0
    for image in images:
        merge.paste(image, (0, offset))
        offset += image.height

    return merge

def limit_scale(image, width, height):
    if image.width > width or image.height > height:
        if image.width/image.height > width/height:
            scale_size = (width, width * image.height//image.width)
        else:
            scale_size = (height * image.width//image.height, height)

        return image.resize(scale_size)
    else:
        return image