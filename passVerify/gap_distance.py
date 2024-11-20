import os
from PIL import Image
import sys


# 获取资源路径
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# 使用后，会自动获取临时文件夹下的资源文件，而不再需要外置静态资源文件C:\Users\vana\AppData\Local\Temp\_MEI286322\./ids-encrypt.js




class SlideCrack(object):
    def __init__(self, gap_img, bg):
        self.gap_img = gap_img
        self.bg = bg

    @staticmethod
    def pixel_is_equal(image1, image2, x, y):
        """
        判断两张图片的像素是否相等,不想等即为缺口位置
        :param image1:
        :param image2:
        :param x:  x坐标
        :param y: y 坐标
        :return:
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 60  # 像素色差
        if abs(pixel1[0]-pixel2[0]) < threshold and abs(pixel1[1]-pixel2[1]) < threshold and abs(pixel1[2]-pixel2[2]) <threshold:
            return True
        else:
            return False

    def get_gap(self, image1, image2):
        """
        获取缺口位置
        :param image1:完整图片
        :param image2: 带缺口的图片
        :return:
        """
        left = 50  # 设置一个起始量,因为验证码一般不可能在左边，加快识别速度
        for i in range(left, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.pixel_is_equal(image1, image2, i, j):
                    left = i
                    return left
        return left

    def run(self):
        
        image1 = Image.open(self.bg)
        image2 = Image.open(self.gap_img)
        # 获取缺口的位置
        gap = self.get_gap(image1, image2)
        return gap


def get_distance():
    img1 =resource_path("gap.png")
    img2=resource_path("full.png")
    gt = SlideCrack(img1, img2)
    val = gt.run()
    os.remove('full.png')
    os.remove('gap.png')
    return val
