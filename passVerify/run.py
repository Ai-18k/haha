import json
import re
import time
import logging
from urllib import request
import execjs
import os
from track import slide_track
from gap_distance import get_distance
from recover import img_recover
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


logging.basicConfig(
    filename=resource_path('captcha.txt'),
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
)

class GeetestCaptcha:
    def __init__(self,gt,challenge,session):
        self.headers = {
            "Host": "api.geetest.com",
            "sec-ch-ua": "\"Chromium\";v=\"124\", \"Microsoft Edge\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
            "DNT": "1.txt",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "script",
            "Referer": "https://www.tianyancha.com/",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
        }
        self.gt = gt
        self.challenge = challenge
        self.c = None
        self.s = None
        self.w = None
        self.session = session

    def __get_cookie(self):
        data = {
            'gt': self.gt,
            'callback': 'geetest_' + str(int(time.time() * 1000))
        }
        self.session.get('https://api.geetest.com/gettype.php', headers=self.headers, params=data)
        data = {
            'gt': self.gt,
            'challenge': self.challenge,
            'lang': 'zh-cn',
            'pt': '0',
            'w': '',
            'callback': 'geetest_' + str(int(time.time() * 1000))
        }
        self.session.get('https://api.geetest.com/ajax.php', params=data, headers=self.headers)

    def __get_image(self):
        data = {
            "is_next": "true",
            "type": "slide3",
            "gt": self.gt,
            "challenge": self.challenge,
            "lang": "zh-cn",
            "https": "true",
            "protocol": "https://",
            "offline": "false",
            "product": "embed",
            "api_server": "api.geetest.com",
            "isPC": "true",
            "width": "100%",
            "callback": "geetest_" + str(int(time.time() * 1000))
        }
        response = self.session.get('https://api.geetest.com/get.php', params=data, headers=self.headers)
        try:
            ret_data = re.findall('.*?({.*?})\)', response.text)[0]
            ret_data = json.loads(ret_data)
            self.c = ret_data["c"]
            self.s = ret_data["s"]
            self.challenge = ret_data['challenge']
            request.urlretrieve('https://static.geetest.com/' + ret_data["bg"], resource_path('gap.jpg'))
            request.urlretrieve('https://static.geetest.com/' + ret_data["fullbg"], resource_path('full.jpg'))
        except Exception as e:
            logging.error('不能获取到图片得url,在get_image函数处:%s' % e)
            raise e

    def __get_track(self):
        img_recover()
        distance = get_distance() - 5
        arr_track = slide_track.get(distance) or slide_track.get(distance - 1) or slide_track.get(
            distance + 1) or slide_track.get(distance + 2) or slide_track.get(distance - 2)
        # current_path = os.path.dirname(__file__)
        # with open(current_path+'/mix.js', 'r', encoding='utf-8')as f:
        with open(resource_path('mix.js'), 'r', encoding='utf-8')as f:
            content = f.read()
        ctx = execjs.compile(content)
        t = arr_track[-1][0]
        n = arr_track[-1][2]
        detail_track = []
        for i in range(len(arr_track) - 1):
            detail_track.append([arr_track[i + 1][0] - arr_track[i][0], arr_track[i + 1][1] - arr_track[i][1],
                                 arr_track[i + 1][2] - arr_track[i][2]])
        self.w = ctx.call('D', arr_track, detail_track, t, n, self.c, self.s, self.gt, self.challenge)

    def __verify(self):
        data = {
            'gt': self.gt,
            'challenge': self.challenge,
            'lang': 'zh-cn',
            'pt': '0',
            'w': self.w,
            'callback': 'geetest_' + str(int(time.time() * 1000))
        }
        response = self.session.get('https://api.geetest.com/ajax.php', params=data, headers=self.headers)
        ret_data = json.loads(re.findall('.*?({.*?})\)',response.text)[0])
        sign=ret_data["validate"]
        return sign


    def run(self):
        # self.__get_gt()
        self.__get_cookie()
        self.__get_image()
        self.__get_track()
        res=self.__verify()
        return res
