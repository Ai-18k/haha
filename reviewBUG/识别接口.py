# _*_ coding:UTF-8 _*
import hashlib

import requests
import json
import base64

img=r"C:\Users\Administrator\Desktop\imgs\word\2dcd912e-7989-11ef-92fe-d0bf9c938902\click_img.png"

with open(img,'rb') as f:
    img_bytes=f.read()

headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "DNT": "1.txt",
    "Origin": "http://124.222.86.140:8000",
    "Pragma": "no-cache",
    "Referer": "http://124.222.86.140:8000/char1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}
url = "http://124.222.86.140:8000/api/charDianxuan/identify"
data = {
    "imageSource": base64.b64encode(img_bytes).decode("utf-8"),
    "dataType": 2,
    "input_chars": "水蜜桃"
}
data = json.dumps(data, separators=(',', ':'))
response = requests.post(url, headers=headers, data=data, verify=False)
print(response.json()["data"]["res"]["crop_centre"])


class CC(object):

    def __init__(self):
        self.username = "15880761625"
        password = "xyq123.xyq".encode('utf8')
        self.password = hashlib.md5(password).hexdigest()
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

res = CC().PostPic(img_bytes, "9501")
print(res["pic_str"])

