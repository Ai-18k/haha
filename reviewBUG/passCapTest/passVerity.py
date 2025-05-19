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
import random
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)

# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)

import base64
import re
import cv2
import ddddocr
import execjs
from loguru import logger
import json
import uuid
from curl_cffi import requests as req
import requests
from passVerify.geetest4_icon import get_icon_position

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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Referer": "https://www.tianyancha.com/",
        }
        uuid1 = uuid.uuid1()
        url = "https://gcaptcha4.geetest.com/load"
        self.session.cookies.set("captcha_v4_user",self.Reqest["cookie_dict"]["captcha_v4_user"])
        logger.info(self.session.cookies)
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
                    bytes_list.append(tag)
                imgs_url = "https://static.geetest.com/" + res["data"]['imgs']
                slide_bytes = requests.get(imgs_url).content
                click_list = get_icon_position(slide_bytes,bytes_list)
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


    def Composite_parameter(self,lot, lotRes, lotNumber):
        key = list(lot.keys())[0]
        def split_lot_number(lot, lotNumber):
            result = []
            split_numbers = []
            for sublist in lot[key]:
                temp = []
                for num in sublist[key]:
                    if isinstance(num, list):
                        temp.append([x + 1 for x in num])
                    else:
                        temp.append(num[key])
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
        if len(res1) == 3:
            return {res1[0]: {res1[1]: {res1[2]: res2[0]}}}
        elif len(res1) == 2:
            return {res1[0]: {res1[1]: res2[0]}}
        elif len(res1) == 1:
            return {res1[0]: res2[0]}
        else:
            raise Exception("is too short or is too long")


    def re_jscodeV1(self,params_list):
        headers = {
            "Host": "static.geetest.com",
            "origin": "https://www.tianyancha.com",
            "User-Agent": self.Reqest["ua"],
            "referer": "https://www.tianyancha.com/",
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
        matche_03 = re.findall(r"!function\(\)\s*\{[\s\S]*?\}\(\),", response.text, re.S)[0]
        pattern = r"!function\(\)\s*\{\s*!(.*?)\}\(\),"  # 匹配 function() 的块
        matche_04 = re.findall(pattern, matche_03, re.S)[0]  # 启用多行模式
        str_code += "var code=" + matche_04 + ";return [this._lib,this.lib._abo]}"
        res = execjs.compile(str_code).call("code")
        return {"head": head, "par_param": res[0], "keys": res[1], "content": response.text, "paramsList": params_list}


    def proxy_list(self):
        # 隧道域名:端口号
        tunnel = "d152.kdltps.com:15818"
        # 用户名密码方式
        username = "t13206952228334"
        password = "wtx4i2in:%d" % random.randint(1, 5)
        proxies = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
        }
        return proxies


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
        data = self.get_1()
        logger.info(data)
        par = self.re_jscodeV1(data)
        with open("mapToDict.js", encoding="utf-8") as file:
            ctx = file.read()
        result = execjs.compile(ctx).call("v", par["keys"])
        param = self.Composite_parameter(result["lot"], result["lotRes"], data["lot_number"])
        logger.info(param)
        jscode = open("w_decode.js", encoding="utf-8").read()
        w = execjs.compile(jscode).call("_fff", data, par["par_param"], param)
        params = {
            "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
            "client_type": "web",
            "lot_number": data["lot_number"],
            "payload": data["payload"],
            "process_token": data["process_token"],
            "payload_protocol": "1",
            "pt": "1",
            "w": w["res"]
        }
        logger.info(self.session.cookies)
        response = self.session.get(url,headers=headers,params=params)
        if response.status_code == 200:
            resp = json.loads(str(response.text).strip("(").strip(")"))
            gen_time = resp["data"]["seccode"]["gen_time"]
            captcha_output = resp["data"]["seccode"]["captcha_output"]
            lot_number = resp["data"]["seccode"]["lot_number"]
            pass_token = resp["data"]["seccode"]["pass_token"]
            self.Reqest["sign"] = w["pow_sign"]
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
              "Host": "www.tianyancha.com",
              "Pragma": "no-cache",
              "Cache-Control": "no-cache",
              "sec-ch-ua-platform": "\"Windows\"",
              "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
              "If-Match": f"\"{IfMatch}\"",
              "sec-ch-ua-mobile": "?0",
              "X-Requested-With": "XMLHttpRequest",
              "User-Agent":self.Reqest["headers"]["User-Agent"],
              "Accept": "*/*",
              "DNT": "1",
              "Content-Type": "application/json; charset=UTF-8",
              "Origin": "https://www.tianyancha.com",
              "Sec-Fetch-Site": "same-origin",
              "Sec-Fetch-Mode": "cors",
              "Sec-Fetch-Dest": "empty",
              "Referer":self.Reqest["headers"]["Referer"],
              "Accept-Language": "zh-CN,zh;q=0.9"
            }
        json_data = {
            "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
            "lot_number": par["lot_number"],
            "pass_token": par["pass_token"],
            "gen_time": par["gen_time"],
            "captcha_output": par["captcha_output"],
        }
        data = json.dumps(json_data, separators=(',', ':'))
        response =requests.post(url,headers=headers,cookies=self.Reqest["cookies"],data=data)
        if response.status_code == 200:
            if response.json()["state"] == "ok":
                logger.success("验证成功，请继续！！！")
                return True
            else:
                logger.error(f"验证失败！响应:{response.json()}")
                raise Exception("验证失败！重试")
        else:
            logger.error("{}：状态异常！！".format(response.status_code))
            raise Exception("验证失败！重试")
