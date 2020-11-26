import random
import itertools
import math
from PIL import Image
from util import *

def k_means(bins, means, k, maxiter=1000, black=True):
    #init
    record = {}
    for color in bins.keys():
        record[color] = -1

    if black:
        means.append((0, 128, 128))

    for _ in range(maxiter):
        done = True
        cluster_sum = [[0, 0, 0] for _ in range(len(means))]
        cluster_size = [0 for _ in range(len(means))]

        #assign
        for color, count in bins.items():
            dists = [distance(color, mean) for mean in means]
            cluster = dists.index(min(dists))

            if record[color] != cluster:
                record[color] = cluster
                done = False

            for i in range(3):
                cluster_sum[cluster][i] += color[i] * count
            cluster_size[cluster] += count

        #update
        for i in range(k):
            if cluster_size[i] > 0:
                means[i] = tuple([cluster_sum[i][j] / cluster_size[i] for j in range(3)])

        if done:
            break

    return means[:k]

def simple_bins(bins, size=16):
    level = 256//size
    temp = {}
    for x in itertools.product(range(size), repeat=3):
        temp[x] = {'size': 0, 'sum': [0, 0, 0]}


    for color, count in bins.items():
        index = tuple([c//level for c in color])
        for i in range(3):
            temp[index]['sum'][i] += color[i] * count
        temp[index]['size'] += count

    result = {}
    for color in temp.values():
        if color['size'] != 0:
            result[tuple([color['sum'][j] / color['size'] for j in range(3)])] = color['size']

    return result

def init_means(bins, k):
    def attenuation(color, target):
        return 1 - math.exp(((distance(color, target)/80)**2) * -1)

    #init
    colors = []
    for color, count in bins.items():
        colors.append([count, color])
    colors.sort(reverse=True)

    #select
    result = []
    for _ in range(k):
        for color in colors:
            if color[1] not in result:
                result.append(color[1])
                break

        for i in range(len(colors)):
            colors[i][0] *= attenuation(colors[i][1], result[-1])

        colors.sort(reverse=True)

    return result

def build_palette(image, k=5, random_init=False, black=True):
    #get colors
    colors = image.getcolors(image.width * image.height)
    print('colors num:', len(colors))

    #build bins
    bins = {}
    for count, pixel in colors:
        bins[pixel] = count
    bins = simple_bins(bins)

    #init means
    if random_init: 
        init = random.sample(list(bins), k)
    else:
        init = init_means(bins, k)

    #k-means
    means = k_means(bins, init, k, black=black)
    means.sort(reverse=True)
    colors = [tuple([int(x) for x in color]) for color in means]
    print('Build palette', colors)
    return colors

def draw_color(color, size=100):
    color = RegularRGB(LABtoRGB(RegularLAB(color)))
    return Image.new('RGB', (size, size), color)

def draw_palette(palette, size=100, horizontal=True):
    images = []
    for color in palette:
        images.append(draw_color(color, size))
    if horizontal:
        return h_merge(images)
    else:
        return v_merge(images)
