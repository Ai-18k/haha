#!/usr/bin/env python
# coding:utf-8

import os
from hashlib import md5
from io import BytesIO
import requests
import json
import uuid
import cv2
import ddddocr
from PIL import Image

def get_1():
    # try:
    headers = {
        "Host": "gcaptcha4.geetest.com",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
        "DNT": "1.txt",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "\"Windows\"",
        "Accept": "*/*",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Dest": "script",
        "Referer": "https://www.tianyancha.com/",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    url = "https://gcaptcha4.geetest.com/load"
    params = {
        # "callback": "geetest_1726673346207",
        "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
        "challenge": "09b9bd49-0407-4550-83c8-6277596c72b7",
        "client_type": "web",
        "lang": "zho"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        res = json.loads(response.text.strip("(").strip(")"))
        type=res["data"]['captcha_type']
        if type=="word":
            print(">>>>>>>>>>>>>>>>>>>>>>>>点选>>>>>>>>>>>>>>")
            imgs="https://static.geetest.com/"+res["data"]['imgs']
            print(imgs)
            q_list=res["data"]['ques']
            ocr = ddddocr.DdddOcr(beta=True)  # 切换为第二套ocr模型
            target_word_list=[]
            for img_url in q_list:
                img=requests.get("https://static.geetest.com/"+img_url).content
                img = Image.open(BytesIO(img))
                white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
                white_bg.paste(img, (0, 0), img)
                result = ocr.classification(white_bg, png_fix=True)
                target_word_list.append(result)
            print(target_word_list)
            return 0,{"type":type,"imgs":imgs,"q_list":q_list,"word_list":target_word_list}

        elif type=="slide":
            print(">>>>>>>>>>>>>>>>>>>>>>>>滑块>>>>>>>>>>>>>>")
            slide_img="https://static.geetest.com/"+res["data"]['slice']
            bg_img="https://static.geetest.com/"+res["data"]['bg']
            ypos=res["data"]['ypos']
            print("slide_img:"+slide_img)
            print("bg_img:"+bg_img,)
            print(ypos)
            return 1,{"type":type,"slide_img":slide_img,"bg_img":bg_img,"ypos":ypos}

# get_1()
def ocr_img(img,filepath):
    det = ddddocr.DdddOcr(det=True)
    with open(img, 'rb') as f:
        image = f.read()
    bboxes = det.detection(image)
    print(bboxes)
    im = cv2.imread(img)
    for bbox in bboxes:
        x1, y1, x2, y2 = bbox
        im = cv2.rectangle(im, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)


    cv2.imwrite(filepath+"/click_img_new.jpg", im)


" 火,56,69|烧,68,136|酥,160,108"
"[[129, 78, 180, 127], [20, 40, 71, 93], [42, 113, 89, 158]]"
# ocr_img("C:\\Users\Administrator\Desktop\imgs\word\\2c5bd7d1-766b-11ef-9543-d0bf9c938902\slide_img.png","C:\\Users\Administrator\Desktop\imgs\word\2c5bd7d1-766b-11ef-9543-d0bf9c938902")


def sile_img(target_bytes,background_bytes):
    slide = ddddocr.DdddOcr(det=False, ocr=False)
    res = slide.slide_match(target_bytes, background_bytes, simple_target=True)["target"][0]+3
    """t透明8到10 px   res["target"][0]"""
    print("》》》》》》》滑块距离：",res)
    return res


def download_img(imgs,filename,type,uuid):
    dir_path = f"C:/Users/Administrator/Desktop/imgs/{type}/{uuid}"
    file_path = os.path.join(dir_path, filename + ".png")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    # 如果文件夹不存在则创建
    if type=="slide":
        with open(file_path,'wb') as f:
            f.write(imgs)
    elif type=="word":
        with open(file_path, 'wb') as f:
            f.write(imgs)
        if filename=="click_img":
            ocr_img(file_path,dir_path)



def main():
    for _ in range(2):
        flg,data=get_1()
        uuid1 = uuid.uuid1()
        if flg:
            res=requests.get(data["slide_img"]).content
            res1 = requests.get(data["bg_img"]).content
            sile_img(res,res1)
            download_img(res, "slide_img",data["type"],uuid1)
            download_img(res1, "bg_img",data["type"],uuid1)
        else:
            for index, img in enumerate(data["q_list"]):
                tag_bytes = requests.get("https://static.geetest.com/" + img).content
                download_img(tag_bytes, str(index), data["type"], uuid1)
            slide_bytes = requests.get(data["imgs"]).content
            res = CC().PostPic(slide_bytes, "9501")
            word_dict = {}
            # print(res["pic_str"].split('|'))
            for index,item in enumerate(res["pic_str"].split('|')):
                word, x, y = item.split(',')
                word_dict[word] = (x, y)
            word_dict["sore"]=data["word_list"]
            print(word_dict)
            download_img(slide_bytes, "click_img", data["type"], uuid1)


class CC(object):

    def __init__(self):
        self.username = "18Klove"
        password = "666666".encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id ='9501'
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1.txt; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()


main()


def local_test(s):
    import os

    def list_folders_in_directory(path):
        for root, dirs, files in os.walk(path):
            for directory in dirs:
                root_path=os.path.join(root, directory)
                yield root_path

    def list_files_in_directory(path):
        # 列出指定目录下的所有文件和文件夹
        items = os.listdir(path)
        # 筛选出文件
        files = [f for f in items if os.path.isfile(os.path.join(path, f))]
        return files

    # 替换为你要搜索的路径
    directory_path = f"C:\\Users\Administrator\Desktop\imgs\{s}"
    for path in list_folders_in_directory(directory_path):
        file_list=list_files_in_directory(path)
        print(file_list)
        if s=="slide":
            bg_path = path + "\\" + file_list[0]
            slide_path = path + "\\" + file_list[1]
            with open(bg_path,"rb") as f1:
                bg_bytes=f1.read()
            with open(slide_path,"rb") as f2:
                target_bytes=f2.read()
            print(slide_path,bg_path)
            print(sile_img(target_bytes,bg_bytes))
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>")
        else:
            slide_path=path+"\slide_img.png"
            print(slide_path)
            with open(slide_path,"rb") as f2:
                slide_bytes=f2.read()
            res=CC().PostPic(slide_bytes,"9501")
            print(res)
            bg_word_dict = {}
            for item in res['pic_str'].split('|'):
                word, x, y = item.split(',')
                bg_word_dict[word] = (x, y)

# s="slide"
# s="word"
# local_test(s)





