# _*_ coding:UTF-8 _*

"""
@author：十一姐
@desc: ddddocr目标识别
@time: 2022/01/09
"""

from io import BytesIO
import ddddocr
from PIL import Image, ImageDraw, ImageFont


class Ddddocr:

    def __init__(self):
        self.ocr = ddddocr.DdddOcr(show_ad=False)
        self.xy_ocr = ddddocr.DdddOcr(det=True, show_ad=False)

    def ddddocr_identify(self, captcha_bytes):
        return self.ocr.classification(captcha_bytes)

    def draw_img(self, content, xy_list):
        """画出图片"""
        # 填字字体
        font_type = "./msyhl.ttc"
        font_size = 20
        font = ImageFont.truetype(font_type, font_size)
        # 识别
        img = Image.open(BytesIO(content))
        draw = ImageDraw.Draw(img)
        words = []
        for row in xy_list:
            # 框字
            x1, y1, x2, y2 = row
            draw.line(([(x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1)]), width=1, fill="red")
            # 裁剪出单个字
            corp = img.crop(row)
            img_byte = BytesIO()
            corp.save(img_byte, 'png')
            # 识别出单个字
            word = self.ocr.classification(img_byte.getvalue())
            words.append(word)
            # 填字
            y = y1 - 30 if y2 > 300 else y2
            draw.text((int((x1 + x2)/2), y), word, font=font, fill="red")
        img.show()
        return words

    def ddddocr_clcik_identify(self, content, crop_size=None):
        """目标检测识别"""
        img = Image.open(BytesIO(content))
        # print(img.size)
        if crop_size:
            img = img.crop(crop_size)
            img_byte = BytesIO()
            img.save(img_byte, 'png')
            content = img_byte.getvalue()
        xy_list = self.xy_ocr.detection(content)
        words = self.draw_img(content, xy_list)
        return dict(zip(words, xy_list))

    def case_demo(self, con):
        """点选识别结果"""
        click_identify_result = self.ddddocr_clcik_identify(con, (0, 0, 344, 344))
        img = Image.open(BytesIO(con))
        img = img.crop((0, 344, 344, 384))
        img_byte = BytesIO()
        img.save(img_byte, 'png')
        identify_words = self.ocr.classification(img_byte.getvalue())
        print(click_identify_result)
        words_dict = {}
        for word in identify_words:
            words_dict[word] = click_identify_result.get(word)
        print(words_dict)
        img_xy = {}
        for key, xy in click_identify_result.items():
            img_xy[key] = (int((xy[0] + xy[2]) / 2), int((xy[1] + xy[3]) / 2))
        print(img_xy)


with open(r'E:\AIProject\Dateset\imgs\word\1a2d6f70-78cb-11ef-80d1-d0bf9c938902\click_img.png', 'rb') as f:
    con1 = f.read()

Ddddocr().case_demo(con1)



