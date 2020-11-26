import sys
import copy
import imageio
from PIL import Image, ImageQt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from palette import *
from util import *
from transfer import *
import cv2
import matplotlib.pyplot as plt
import os
from os.path import isfile, join
# isGray = False

class ImageLabel(QLabel):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super(ImageLabel, self).__init__(parent, flags)
        self.bind_image = None

    def setImage(self, image):
        self.bind_image = ImageQt.ImageQt(image)
        self.setPixmap(QPixmap.fromImage(self.bind_image))
        # self.setScaledContents(True);
        # self.setSizePolicy( QSizePolicy.Ignored, QSizePolicy.Ignored )

class PaletteLabel(ImageLabel):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super(PaletteLabel, self).__init__(parent, flags)
        self.palette_index = -1
        self.bind_color = None

    def setColor(self, color):
        self.bind_color = color
        self.setImage(draw_color(color))
        self.repaint()

    def mousePressEvent(self, event):
        #init
        global image_rgb_m, image_lab_m, palette_m

        #get color
        current = QColor(*RegularRGB(LABtoRGB(RegularLAB(self.bind_color))))
        print ("Color is ", current)
        color = QColorDialog.getColor(initial=current, options=QColorDialog.DontUseNativeDialog)
        if not color.isValid():
            return

        RGB = color.red(), color.green(), color.blue()
        # print("RGB = ", RGB)
        LAB = ByteLAB(RGBtoLAB(RGB))
        print('Set palette color', self.palette_index, RGB, LAB)
        # print("ModeFlag = ", mode_flag, "LumFlag = ", luminance_flag)
        # print("Org P = ", palette, "Mod P = ", palette_m)

        #modify palette_m
        if mode_flag and luminance_flag:
            palette_m = modify_luminance(palette_m, self.palette_index, LAB[0])
        palette_m[self.palette_index] = LAB

        #modify original palette
        if not mode_flag:
            palette[self.palette_index] = LAB

        #modify palette labels
        for i in range(len(palette_m)):
            labels_palette[i].setColor(palette_m[i])

        #transfer image
        if mode_flag:
            print('Original palette', [RegularRGB(LABtoRGB(RegularLAB(color))) for color in palette])
            print('Modified palette', [RegularRGB(LABtoRGB(RegularLAB(color))) for color in palette_m])
            image_lab_m = image_transfer(image_lab, palette, palette_m, sample_level=10, luminance_flag=luminance_flag)
            image_rgb_m = lab2rgb(image_lab_m)
            label_image.setImage(limit_scale(image_rgb_m, width, height))

def is_grey_scale(img_path):
    img = Image.open(img_path).convert('RGB')
    w,h = img.size
    for i in range(w):
        for j in range(h):
            r,g,b = img.getpixel((i,j))
            if r != g != b: return False
    return True

def load_image(label_image, labels_palette):
    #init
    global image_rgb, image_rgb_m, image_lab, image_lab_m, palette, palette_m, palette_bak

    #get image
    image_name = QFileDialog.getOpenFileName()[0]
    if image_name == '':
        return

    isGray = is_grey_scale(image_name)
    print("isGray : " ,isGray)
    

    image_rgb = Image.open(image_name)
    im = image_rgb
    # print("Img Shape = ", im.size)    
    image_rgb = image_rgb.resize((round(im.size[0]*450/im.size[1]), round(im.size[1]*450/im.size[1])), Image.ANTIALIAS)
    print("Img Shape = ", image_rgb.size)
    image_rgb = image_rgb.convert("RGBA")
    print(image_name, image_rgb.format, image_rgb.size, image_rgb.mode)

    #get palette
    image_lab = rgb2lab(image_rgb)
    palette = build_palette(image_lab, len(labels_palette))
    # for color in palette: 
    #     print('LAB:', color, 'LAB_fix:', RegularLAB(color), 'RGB:', LABtoRGB(RegularLAB(color)))

    #set image label
    label_image.setImage(image_rgb)

    #set palette label
    for i in range(len(palette)):
        labels_palette[i].setColor(palette[i])

    #copy object
    image_rgb_m = copy.deepcopy(image_rgb)
    image_lab_m = copy.deepcopy(image_lab)
    palette_m = copy.deepcopy(palette)
    palette_bak = copy.deepcopy(palette)

def load_video(label_image, labels_palette):
    #init
    global image_rgb, image_rgb_m, image_lab, image_lab_m, palette, palette_m, palette_bak

    #get image
    vid_name = QFileDialog.getOpenFileName()[0]
    if vid_name == '':
        return
    

    cap = cv2.VideoCapture(vid_name)
    print(cap)
    img = []
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img.append(Image.fromarray(frame))
    cap.release()
    image_rgb = img
    im = image_rgb[0]
    # print("Img Shape = ", im.size)    
    image_rgb[0] = image_rgb[0].resize((round(im.size[0]*450/im.size[1]), round(im.size[1]*450/im.size[1])), Image.ANTIALIAS)
    print("Img Shape = ", image_rgb[0].size, "Vid size = ", len(image_rgb))
    print(vid_name, image_rgb[0].format, image_rgb[0].size, image_rgb[0].mode)

    #get palette
    image_lab = rgb2lab(image_rgb[0])
    palette = build_palette(image_lab, len(labels_palette))
    # for color in palette: 
    #     print('LAB:', color, 'LAB_fix:', RegularLAB(color), 'RGB:', LABtoRGB(RegularLAB(color)))

    #set image label
    label_image.setImage(image_rgb[0])

    #set palette label
    for i in range(len(palette)):
        labels_palette[i].setColor(palette[i])

    #copy object
    image_rgb_m = copy.deepcopy(image_rgb[0])
    image_lab_m = copy.deepcopy(image_lab)
    palette_m = copy.deepcopy(palette)
    palette_bak = copy.deepcopy(palette)

def save_image():
    #get image
    global image_rgb_m, image_lab_m, palette_m, palette, image_rgb
    save_name = QFileDialog.getSaveFileName()[0]
    if save_name == '':
        save_name = 'Out'

    j = 0
    if type(image_rgb) is list:
        ans = []
        for i in range(0,300):
            image_lab = rgb2lab(image_rgb[i])
            image_lab_m = image_transfer(image_lab, palette, palette_m, sample_level=10, luminance_flag=luminance_flag)
            temp = cv2.cvtColor(numpy.array(lab2rgb(image_lab_m)), cv2.COLOR_RGB2BGR)
            plt.imshow(temp,cmap='gray')
            # plt.show()
            print(temp)
            # temp.convert('RGB').save("a"+str(i)+".jpg")
            path1 = './Images/'
            cv2.imwrite(os.path.join(path1 , "a"+str(i)+".jpg"),temp)
            # cv2.imwrite("a"+str(i)+".jpg",temp)

            ans.append(temp)
            
            j+= 1
            print("No. : ", j)
        # size = (ans[0].shape[1], ans[0].shape[0])
        # print("Size :", size)
        pathIn= './Images/'
        frame_array = []
        files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]

        #for sorting the file names properly
        files.sort(key = lambda x: x[5:-4])
        fps = 24
        files.sort()
        pathOut = 'video.avi'
        frame_array = []
        files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]#for sorting the file names properly
        files.sort(key = lambda x: x[5:-4])
        for i in range(len(files)):
            filename=pathIn + files[i]
            #reading each files
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width,height)
        
            #inserting the frames into an image array
            frame_array.append(img)
        out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
        
        for i in range(len(frame_array)):
        # writing to a image array
            out.write(frame_array[i])
        out.release()

        # file = open('read.txt', 'w') 
        # file.write(ans) 
        # file.close() 

        # out = cv2.VideoWriter(save_name,cv2.VideoWriter_fourcc(*'DIVX'), 0.5, size)
        # j = 0
        # for i in range(len(ans)):
        #     # writing to a image array
        #     out.write(ans[i])
        #     j+= 1
        #     print("Writing : ", j)
        # out.release()
    else:
        image_rgb_m.convert('RGB').save(save_name)

    # image_lab_m = image_transfer(image_lab, palette, palette_m, sample_level=10, luminance_flag=luminance_flag)
    # image_rgb_m = lab2rgb(image_lab_m)


def reset():
    #init
    global image_rgb_m, image_lab_m, palette_m, palette

    #reset object
    image_rgb_m = copy.deepcopy(image_rgb)
    image_lab_m = copy.deepcopy(image_lab)
    palette_m = copy.deepcopy(palette_bak)
    palette = copy.deepcopy(palette_bak)

    #reset GUI
    label_image.setImage(limit_scale(image_rgb, width, height))
    for i in range(len(palette)):
        labels_palette[i].setColor(palette[i])

def mode_flag_changed(box):
    global mode_flag
    mode_flag = box.currentData()


if __name__ == '__main__':
    #init
    width = 900
    height = 600
    palette_num = 5
    mode_flag = True
    luminance_flag = False
    app = QApplication(sys.argv)

    #main widget
    widget = QWidget()
    widget.resize(width, height)
    # widget.showMaximized()
    widget.setWindowTitle('Tool')
    widget.show()

    #label
    label_image = ImageLabel()
    label_image.setAlignment(Qt.AlignCenter)
    # global labels_palette
    labels_palette = []
    for i in range(palette_num):
        labels_palette.append(PaletteLabel())
        labels_palette[-1].setAlignment(Qt.AlignCenter)
        labels_palette[-1].palette_index = i
        labels_palette[-1].setPixmap(QPixmap(100, 100))
        labels_palette[-1].pixmap().fill(QColor(0, 0, 0, 0))
        labels_palette[-1].setScaledContents(False);

    #button
    btn_load_image = QPushButton('Load image')
    btn_load_image.clicked.connect(lambda: load_image(label_image, labels_palette))
    btn_load_image.show()

    btn_load_video = QPushButton('Load video')
    btn_load_video.clicked.connect(lambda: load_video(label_image, labels_palette))
    btn_load_video.show()

    btn_save = QPushButton('Save image')
    btn_save.clicked.connect(lambda: save_image())
    btn_save.show()

    btn_reset = QPushButton('Reset')
    btn_reset.clicked.connect(lambda: reset())
    btn_reset.show()

    #combobox
    box_mode_flag = QComboBox()
    box_mode_flag.activated.connect(lambda: mode_flag_changed(box_mode_flag))
    box_mode_flag.addItem('Normal mode', QVariant(True))
    box_mode_flag.addItem('Palette edit mode', QVariant(False))
    box_mode_flag.setCurrentIndex(0)
    box_mode_flag.show()

    #layout
    layout_image = QHBoxLayout()
    layout_image.addWidget(label_image)

    # print("isGray = ", isGray)

    layout_palette = QHBoxLayout()
    for label in labels_palette:
        layout_palette.addWidget(label)

    layout_btn = QHBoxLayout()
    layout_btn.addWidget(btn_load_image)
    layout_btn.addWidget(btn_load_video)
    layout_btn.addWidget(btn_save)
    layout_btn.addWidget(btn_reset)

    layout = QVBoxLayout()
    layout.addLayout(layout_image)
    layout.addLayout(layout_palette)
    layout.addLayout(layout_btn)
    layout.addWidget(box_mode_flag)

    widget.setLayout(layout)

    app.exec()
