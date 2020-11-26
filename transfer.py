import math
import itertools
import time
import numpy.linalg
from util import *
from multiprocessing import Pool, cpu_count

def modify_luminance(original_p, index, new_l):
    modified_p = original_p[:]
    # print(modified_p)

    modified_p[index] = (new_l, *modified_p[index][-2:])
    # print(modified_p)
    for i in range(index+1, len(original_p)):
        # print("i = ", i, "Before Pal = ", modified_p)
        modified_p[i] = (min(modified_p[i][0], modified_p[i-1][0]), *modified_p[i][-2:])
        # print("i = ", i, "After Pal = ", modified_p)
    for i in range(index-1, -1, -1):
        # print("i = ", i, "Before Pal = ", modified_p)
        modified_p[i] = (max(modified_p[i][0], modified_p[i+1][0]), *modified_p[i][-2:])
        # print("i = ", i, "After Pal = ", modified_p)

    return modified_p

def luminance_transfer(color, original_p, modified_p):
    # print(color[0])
    def interpolation(xa, xb, ya, yb, z):
        return (ya*(xb-z) + yb*(z-xa)) / (xb - xa)

    l = color[0]
    original_l = [100] + [l for l, a, b in original_p] + [0]
    modified_l = [100] + [l for l, a, b in modified_p] + [0]
    # print(len(modified_l))
    if l > 100:
        return 100
    elif l <= 0:
        return 0
    else:
        for i in range(len(original_l)):
            if original_l[i] == l:
                return modified_l[i]
            elif original_l[i] > l > original_l[i+1]:
                return interpolation(original_l[i], original_l[i+1], modified_l[i], modified_l[i+1], l)

class Vec3:
    def __init__(self, data):
        self.data = data

    def __add__(self, other):
        return Vec3([x + y for x, y in zip(self.data, other.data)])

    def __sub__(self, other):
        return Vec3([x - y for x, y in zip(self.data, other.data)])

    def __mul__(self, other):
        return Vec3([x * other for x in self.data])

    def __truediv__(self, other):
        return Vec3([x / other for x in self.data])

    def len(self):
        return (sum([x**2 for x in self.data]))**0.5

def single_color_transfer(color, original_c, modified_c):
    def get_boundary(origin, direction, k_min, k_max, iters=20):
        start = origin + direction * k_min
        end = origin + direction * k_max
        for _ in range(iters):
            mid = (start + end) / 2
            if ValidLAB(mid.data) and ValidRGB(LABtoRGB(mid.data)):
                start = mid
            else:
                end = mid
        return (start + end) / 2

    #init
    color = Vec3(color)
    original_c = Vec3(original_c)
    modified_c = Vec3(modified_c)
    offset = modified_c - original_c

    #get boundary
    c_boundary = get_boundary(original_c, offset, 1, 255)
    naive = (color + offset).data
    if ValidLAB(naive) and ValidRGB(LABtoRGB(naive)):
        boundary = get_boundary(color, offset, 1, 255)
    else:
        boundary = get_boundary(modified_c, color - original_c, 0, 1)

    #transfer
    if (boundary - color).len() == 0:
        result = color
    elif (boundary - color).len() < (c_boundary - original_c).len():
        result = color + (boundary - color) * (offset.len() / (c_boundary - original_c).len())
    else:
        result = color + (boundary - color) * (offset.len() / (boundary - color).len())

    return result

def calc_weights(color, original_p):
    def mean_distance(original_p):
        dists = []
        for a, b in itertools.combinations(original_p, 2):
            dists.append(distance(a, b))
        return sum(dists) / len(dists)

    def gaussian(r, md):
        return math.exp(((r/md)**2) * -0.5)

    #init
    md = mean_distance(original_p)

    #get phi and lambda
    matrix = []
    for i in range(len(original_p)):
        temp = []
        for j in range(len(original_p)):
            temp.append(gaussian(distance(original_p[j], original_p[i]), md))
        matrix.append(temp)
    phi = numpy.array(matrix)
    lamb = numpy.linalg.inv(phi)

    #calc weights
    weights = [0 for _ in range(len(original_p))]
    for i in range(len(original_p)):
        for j in range(len(original_p)):
            weights[i] += lamb[i][j] * gaussian(distance(color, original_p[j]), md)

    #normalize weights
    weights = [w if w >=0 else 0 for w in weights]
    w_sum = sum(weights)
    weights = [w/w_sum for w in weights]

    return weights

def multiple_color_transfer(color, original_p, modified_p):
    #single color transfer
    color_st = []
    for i in range(len(original_p)):
        color_st.append(single_color_transfer(color, original_p[i], modified_p[i]))

    #get weights
    weights = calc_weights(color, original_p)

    #calc result
    color_mt = Vec3([0, 0, 0])
    for i in range(len(original_p)):
        color_mt = color_mt + color_st[i] * weights[i]

    return color_mt.data

def RGB_sample_color(size=16):
    assert(size >= 2)

    levels = [i * (255/(size-1)) for i in range(size)]
    colors = []
    for r, g, b in itertools.product(levels, repeat=3):
        colors.append((r, g, b))

    return colors

def nearest_color(target, level, levels):
    nearest_level = []
    for ch in target:
        index = ch / level
        nearest_level.append((levels[math.floor(index)], levels[math.ceil(index)]))

    return nearest_level

def trilinear_interpolation(target, corners, sample_color_map):
    #calc rates
    RGBr = []
    for i in range(3):
        temp = (target[i] - corners[i][0]) / (corners[i][1] - corners[i][0]) if corners[i][0] != corners[i][1] else 0
        RGBr.append((1 - temp, temp))

    rates = []
    for Rr, Gr, Br in itertools.product(*RGBr):
        rates.append(Rr * Gr * Br)

    #calc result
    result = [0, 0, 0]
    for color, rate in zip(itertools.product(*corners), rates):
        sc = sample_color_map[color]
        for i in range(3):
            result[i] += sc[i] * rate

    return result

def luminance_transfer_mt(args):
    return luminance_transfer(*args)

def multiple_color_transfer_mt(args):
    return multiple_color_transfer(*args)

def trilinear_interpolation_mt(args):
    return trilinear_interpolation(*args)

def image_transfer(image, original_p, modified_p, sample_level=16, luminance_flag=False):
    t = time.time()
    #init
    original_p = [RegularLAB(c) for c in original_p]
    modified_p = [RegularLAB(c) for c in modified_p]
    level = 255 / (sample_level - 1)
    levels = [i * (255/(sample_level-1)) for i in range(sample_level)]
    # print("Org = ", original_p, " Mod = ", modified_p, "Lev = ", level, "Dont Know", levels)

    #build sample color map
    print('Build sample color map')
    t2 = time.time()
    sample_color_map = {}
    sample_colors = RGB_sample_color(sample_level)
    # print(sample_colors)

    args = []
    for color in sample_colors:
        args.append((RegularLAB(color), original_p, modified_p))
    # print(args[0])

    if luminance_flag:
        with Pool(cpu_count()-1) as pool:
            l = pool.map(luminance_transfer_mt, args)
            lab = pool.map(multiple_color_transfer_mt, args)

        for i in range(len(sample_colors)):
            sample_color_map[sample_colors[i]] = ByteLAB((l[i], *lab[i][-2:]))
    else:
        with Pool(cpu_count()-1) as pool:
            lab = pool.map(multiple_color_transfer_mt, args)

        for i in range(len(sample_colors)):
            sample_color_map[sample_colors[i]] = ByteLAB(lab[i])

    print('Build sample color map time', time.time() - t2)
    t2 = time.time()

    #build color map
    print('Build color map')
    color_map = {}
    colors = image.getcolors(image.width * image.height)

    args = []
    for _, color in colors:
        nc = nearest_color(color, level, levels)
        args.append((color, nc, sample_color_map))
    with Pool(cpu_count()-1) as pool:
        inter_result = pool.map(trilinear_interpolation_mt, args)

    for i in range(len(colors)):
        color_map[colors[i][1]] = tuple([int(x) for x in inter_result[i]])
    print('Build color map time', time.time() - t2)
    t2 = time.time()

    #transfer image
    print('Transfer image')
    result = Image.new('LAB', image.size)
    result_pixels = result.load()
    image_pixels = image.load()
    for i in range(image.width):
        for j in range(image.height):
            result_pixels[i, j] = color_map[image_pixels[i, j]]
    print('Transfer image time', time.time() - t2)

    print('Total time', time.time() - t)
    return result
