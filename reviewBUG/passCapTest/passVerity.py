# _*_ coding:UTF-8 _*
"""
@FileName：success_code.py
@Description：
@Author：18k
@Time：2024/4/14 17:38
@Department：部门
@Website：站点
@Copyright：©2019-2024 职业
:return:
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)

# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)

import base64
import io
import re
import time
import cv2
import ddddocr
import execjs
from loguru import logger
import json
import uuid
from retrying import retry
from curl_cffi import requests as req
import requests


class CC1:
    def PostPic(self, final_image):
        out_buff = io.BytesIO()
        final_image.save(out_buff, format='PNG')
        byte_pic = out_buff.getvalue()
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "DNT": "1",
            "Origin": "http://192.168.5.181:8011",
            "Pragma": "no-cache",
            "Referer": "http://192.168.5.181:8011/char1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        url = "http://192.168.5.181:8011/dianxuan/identify"
        data = {
            "dataType": 2,
            "imageSource": base64.b64encode(byte_pic).decode('utf-8'),
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            data = response.json()
            _crop = data["data"]["res"]["crop_centre"]
            return _crop
        else:
            raise Exception("链接失效")


class CC:
    def PostPic(self, pic_list):
        if len(pic_list) == 4:
            pic_list.append("")
        tmp = str(time.time())
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        }
        url = "http://192.168.5.181:10121/geetest4_icon/gradio_api/queue/"
        # url = "http://127.0.0.1:1012/geetest4_icon/gradio_api/queue/"
        params = {"": ""}
        data = {
            "data": pic_list,
            "event_data": None,
            "fn_index": 1,
            "trigger_id": 121,
            "session_hash": tmp
        }
        data = json.dumps(data, separators=(',', ':'))
        requests.post(url + "join", headers=headers, params=params, data=data, verify=False)
        param = {
            "session_hash": tmp
        }
        time.sleep(0.1)
        response = requests.get(url + "data", headers=headers, params=param, verify=False)
        message_count = 0  # 初始化计数器
        # 逐行读取事件流数据
        for line in response.iter_lines(decode_unicode=True):
            if line:  # 跳过空行
                if line.startswith("data:"):
                    data = line[5:].strip()  # 去掉 "data:" 前缀并清理空格
                    message_count += 1
                    # 检查是否已接收到第三条消息
                    if message_count == 3:
                        xy = []
                        plan = json.loads(data)["output"]["data"][1]
                        for crop in plan:
                            x1, y1, x2, y2 = crop
                            xy.append([(x1 + x2) / 2, (y1 + y2) / 2])
                        return xy


# @retry(wait_fixed=1000)
def verify(content):
    url = "http://api.jfbym.com/api/YmServer/customApi"
    data = {
        ## 关于参数,一般来说有3个;不同类型id可能有不同的参数个数和参数名,找客服获取
        "token": "6EubemuI0kmsMzHS6BjgVTBwMEu4uADPuXnJ30SwDr4",
        "type": "30114",
        "image": base64.b64encode(content).decode(),
        "extra": "je4_phrase"
    }
    _headers = {
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, headers=_headers, json=data)
    print(response)
    if response.status_code == 200:
        data = response.json()
        x_coord = data["data"]["data"]
        xy = [str(i).split(",") for i in str(x_coord).split("|")]
        result = [[int(x) for x in sublist] for sublist in xy]
        return result
    else:
        raise Exception("识别失败")


ocr = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
ocr1 = ddddocr.DdddOcr(beta=True, show_ad=False)  # 切换为第二套ocr模型
ocr2 = ddddocr.DdddOcr(det=True, show_ad=False)


class Demo:

    def __init__(self, Reqest):
        self.session = requests.Session()
        self.Reqest = Reqest


    def ocr_img(self, img, filepath):
        with open(img, 'rb') as f:
            image = f.read()
        bboxes = ocr2.detection(image)
        # print(bboxes)
        im = cv2.imread(img)
        for bbox in bboxes:
            x1, y1, x2, y2 = bbox
            im = cv2.rectangle(im, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)
        cv2.imwrite(filepath + "/click_img_new.jpg", im)


    def download_img(self, imgs, filename, type, uuid):
        dir_path = f"E:/AIProject/Datesets/imgs/{type}/{uuid}"
        file_path = os.path.join(dir_path, filename + ".png")
        # 如果文件夹不存在则创建
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if type == "phrase":
            with open(file_path, 'wb') as f:
                f.write(imgs)
        elif type == "icon":
            with open(file_path, 'wb') as f:
                f.write(imgs)
            if filename == "click_img":
                self.ocr_img(file_path, dir_path)


    def get_1(self):
        # try:
        headers = {
            "Host": "gcaptcha4.geetest.com",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
            "DNT": "1",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "script",
            "Referer": "https://www.tianyancha.com/",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        uuid1 = uuid.uuid1()
        url = "https://gcaptcha4.geetest.com/load"
        self.session.cookies.set("captcha_v4_user",self.Reqest["cookie_dict"]["captcha_v4_user"])
        params = {
            "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
            "challenge": uuid1,
            "client_type": "web",
            "lang": "zho"
        }
        response = self.session.get(url, headers=headers, params=params)
        if response.status_code == 200:
            res = json.loads(response.text.strip("(").strip(")"))
            type = res["data"]['captcha_type']
            lot_number =res["data"]["lot_number"]
            process_token = res["data"]["process_token"]
            pow_detail = res["data"]["pow_detail"]
            pow_detail = [pow_detail[i] for i in pow_detail if isinstance(pow_detail, dict)]
            payload =res["data"]["payload"]
            static_path =res["data"]["static_path"]
            params_list = {
                "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
                "lot_number": lot_number,
                "process_token": process_token,
                "pow_detail": pow_detail,
                "payload": payload,
                "static_path": static_path
            }
            if type == "icon":
                print(">>>>>>>>>>>>>>>>>>>>>图形验证>>>>>>>>>>>>>>")
                q_list = res["data"]['ques']
                bytes_list = []
                for index, img_url in enumerate(q_list):
                    tag = requests.get("https://static.geetest.com/" + img_url).content
                    word_pic = base64.b64encode(tag).decode("utf-8")
                    bytes_list.append(word_pic)
                imgs_url = "https://static.geetest.com/" + res["data"]['imgs']
                slide_bytes = requests.get(imgs_url).content
                bytes_list = [base64.b64encode(slide_bytes).decode("utf-8")] + bytes_list
                click_list = CC().PostPic(bytes_list)
                click_smark = []
                for _word in click_list:
                    click_smark.append([round(int(_word[0]) * 100 / 3), round(int(_word[1]) * 50)])
                logger.info(click_smark)
                # self.download_img(slide_bytes, "click_img", type, uuid1)
                params_list["smark"] = click_smark
                params_list["type"] = "icon"
            elif type == "phrase":
                print(">>>>>>>>>>>>>>>>>>>>>>语序验证>>>>>>>>>>>>>>")
                bg_url = "https://static.geetest.com/" + res["data"]['imgs']
                bg_bytes = requests.get(bg_url).content
                self.download_img(bg_bytes, "bg_img", type, uuid1)
                click_list=verify(bg_bytes)
                click_smark = []
                for _word in click_list:
                    click_smark.append([round(int(_word[0]) * 100 / 3), round(int(_word[1]) * 50)])
                logger.info(click_smark)
                params_list["smark"] = click_smark
                params_list["type"] = "phrase"
            else:
                logger.error(type)
                print(response.json())
            return params_list

    def Composite_parameter(self,lotNumber):
        lot = {
            "$_JP": [
                {
                    "$_JP": [
                        {
                            "$_JP": [
                                25
                            ]
                        },
                        {
                            "$_JP": [
                                28
                            ]
                        },
                        {
                            "$_JP": [
                                22
                            ]
                        },
                        {
                            "$_JP": [
                                18
                            ]
                        }
                    ]
                },
                {
                    "$_JP": [
                        {
                            "$_JP": [
                                1,
                                4
                            ]
                        },
                        {
                            "$_JP": [
                                4,
                                7
                            ]
                        }
                    ]
                }
            ]
        }
        lotRes = {
            "$_JP": [
                {
                    "$_JP": [
                        {
                            "$_JP": [
                                0,
                                5
                            ]
                        }
                    ]
                }
            ]
        }
        def split_lot_number(lot, lotNumber):
            result = []
            split_numbers = []
            for sublist in lot["$_JP"]:
                temp = []
                for num in sublist["$_JP"]:
                    if isinstance(num, list):
                        temp.append([x + 1 for x in num])
                    else:
                        temp.append(num["$_JP"])
                result.append(temp)
            for sublist in result:
                temp = ""
                for num in sublist:
                    if len(num) > 1:
                        num[-1] += 1
                        temp += lotNumber[num[0]:num[1]]
                    else:
                        temp += lotNumber[num[0]]
                split_numbers.append(temp)
            return split_numbers
        res1 = split_lot_number(lot, lotNumber)
        res2 = split_lot_number(lotRes, lotNumber)
        return {res1[0]: {res1[1]: res2[0]}}


    def re_js_code(self):
        params_list = self.get_1()
        headers = {
            "Host": "static.geetest.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                         "Chrome\";v=\"114\"",
            "origin": "https://www.tianyancha.com",
            "dnt": "1",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": self.Reqest["ua"],
            "sec-ch-ua-platform": "\"Windows\"",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "script",
            "referer": "https://www.tianyancha.com/",
            "accept-language": "zh-CN,zh;q=0.9"
        }
        url = "https://static.geetest.com" + params_list["static_path"] + "/js/gcaptcha4.js"
        response = self.session.get(url, headers=headers)
        str_code = ""
        match = re.search(r'(.*?)\.', response.text, re.S)
        head = match.group().strip(".")
        matche_01 = re.findall(rf"{head}\..*?\}}\(\);", response.text, re.S)
        str_code += matche_01[0] + matche_01[1]
        matche_02 = re.findall(rf'{head}\..*?}};', response.text, re.S)
        str_code += matche_02[2] + matche_02[3] + f"function {head}() {{}};"
        pattern = r'!function\s*\(\)\s*{[^}]*}()'
        matche_03 = re.search(pattern, response.text, re.S)
        text = matche_03.group()
        matche_04 = re.search(r"var.*?.shift\(\);", text, re.S)
        str_code += "function get_param(){" + matche_04.group()
        pattern = r'\{\s*"(\\u[0-9a-fA-F]+)+":\s*[_\w]+\([0-9]+\)\s*\}'
        # 查找匹配项
        match = re.search(pattern, text)
        if match:
            matche_05 = match.group(0)
        else:
            matche_05 = re.search(r'\{"(.*?)}', text, re.S)
        try:
            str_code1 = str_code + "return " + matche_05.strip() + "};}"
            res = execjs.compile(str_code1).call("get_param")
        except:
            try:
                str_code2 = str_code + "return " + matche_05.strip() + "}"
                res = execjs.compile(str_code2.encode().decode("utf-8")).call("get_param")
            except:
                str_code3 = str_code + "return " + matche_05.strip()+ "};"
                res = execjs.compile(str_code3).call("get_param")
        return {"par_param": res, "par_data": params_list}


    def proxy_list(self):
        proxyAddr = "tun-yowmaw.qg.net:17228"
        authKey = "17C8C7A6"
        password = "F825824D03DC"
        proxyUrl = "http://%(user)s:%(password)s@%(server)s" % {
            "user": authKey,
            "password": password,
            "server": proxyAddr,
        }
        proxies = {
            "http": proxyUrl,
            "https": proxyUrl,
        }
        return proxies
        # return None


    def get_2(self):
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Pragma": "no-cache",
            "Referer": "https://www.tianyancha.com/",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": self.Reqest["ua"],
            "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", "
                         "\"Chromium\";v=\"123\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://gcaptcha4.geetest.com/verify"
        # par = self.re_js_code()
        par = self.get_1()
        par["par_param"] = {'fOL0': 'PAVJ'}
        param = self.Composite_parameter(par["lot_number"])
        print(param)
        jscode = open("w_decode.js", encoding="utf-8").read()
        data = execjs.compile(jscode).call("_fff", par, par["par_param"], param)
        params = {
            "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
            "client_type": "web",
            "lot_number": par["lot_number"],
            "payload": par["payload"],
            "process_token": par["process_token"],
            "payload_protocol": "1",
            "pt": "1",
            "w": data["res"]
        }
        response = self.session.get(url,headers=headers,params=params)
        if response.status_code == 200:
            resp = json.loads(str(response.text).strip("(").strip(")"))
            gen_time = resp["data"]["seccode"]["gen_time"]
            captcha_output = resp["data"]["seccode"]["captcha_output"]
            lot_number = resp["data"]["seccode"]["lot_number"]
            pass_token = resp["data"]["seccode"]["pass_token"]
            self.Reqest["sign"] = data["pow_sign"]
            params_list1 = {
                "lot_number": lot_number,
                "pass_token": pass_token,
                "gen_time": gen_time,
                "captcha_output": captcha_output
            }
            return params_list1
        else:
            logger.error(f"请求状态码:{response.status_code}")


    # @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def passVerity(self, sign):
        par = self.get_2()
        with open("4.js", encoding="utf-8") as f:
            jscode = f.read()
        IfMatch = execjs.compile(jscode).call("verify", par["lot_number"], sign)
        logger.info(IfMatch)
        url = "https://www.tianyancha.com/sorry/verifyCaptcha4.json"
        headers = {
            'Host': 'www.tianyancha.com',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua': self.Reqest["headers"]["sec-ch-ua"],
            'If-Match': f"{IfMatch}",
            'sec-ch-ua-mobile': '?0',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': self.Reqest["headers"]["User-Agent"],
            'Accept': '*/*',
            'DNT': '1',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://www.tianyancha.com',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer':self.Reqest["headers"]["Referer"],
            'Accept-Language': 'zh-CN,zh;q=0.9',
            }
        json_data = {
            "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
            "lot_number": par["lot_number"],
            "pass_token": par["pass_token"],
            "gen_time": par["gen_time"],
            "captcha_output": par["captcha_output"],
        }
        data = json.dumps(json_data, separators=(',', ':'))
        response = requests.post(url, cookies=self.Reqest["cookies"],headers=headers, data=data)
        if response.status_code == 200:
            if response.json()["state"] == "ok":
                return True
            else:
                logger.error(f"验证失败！响应:{response.json()}")
                raise Exception("验证失败！重试")
        else:
            logger.error("{}：状态异常！！".format(response.status_code))
            raise Exception("验证失败！重试")
