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
# from curl_cffi import requests
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
        # import requests
        tmp = str(time.time())
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        }
        url = "http://192.168.5.181:10121/geetest4_icon/gradio_api/queue/"
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


@retry(wait_fixed=1)
def verify(content):
    url = "http://api.jfbym.com/api/YmServer/customApi"
    data = {
        ## 关于参数,一般来说有3个;不同类型id可能有不同的参数个数和参数名,找客服获取
        "token": "UquqP253oi04KuvBMFYVmRcx_1lJl7Q1FxIwknR9IpU",
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
        self.get_cookie_csrf()
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
        _uuid = uuid.uuid1()
        url = "https://gcaptcha4.geetest.com/load"
        params = {
            "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
            "challenge": _uuid,
            # "challenge": "09d9c310-e098-467a-8b6c-c61ae6642e3c",
            "client_type": "web",
            "lang": "zho"
        }
        response = self.session.get(url, headers=headers, params=params)
        if response.status_code == 200:
            cookies = response.cookies.get("captcha_v4_user")
            res = json.loads(response.text.strip("(").strip(")"))
            # print(res)
            type = res["data"]['captcha_type']
            lot_number = res.get("data").get("lot_number")
            process_token = res.get("data").get("process_token")
            pow_detail = res.get("data").get("pow_detail")
            pow_detail = [pow_detail[i] for i in pow_detail if isinstance(pow_detail, dict)]
            payload = res.get("data").get("payload")
            static_path = res.get("data").get("static_path")
            params_list = {
                "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
                "lot_number": lot_number,
                "process_token": process_token,
                "pow_detail": pow_detail,
                "payload": payload,
                "cookies": cookies,
                "static_path": static_path
            }
            uuid1 = uuid.uuid1()
            if type == "icon":
                print(">>>>>>>>>>>>>>>>>>>>>图形验证>>>>>>>>>>>>>>")
                q_list = res["data"]['ques']
                bytes_list = []
                for index, img_url in enumerate(q_list):
                    tag = requests.get("https://static.geetest.com/" + img_url).content
                    # self.download_img(tag, str(index), type, uuid1)
                    # word_pic = ImageProcess.wordprocess(tag)
                    word_pic = base64.b64encode(tag).decode("utf-8")
                    bytes_list.append(word_pic)
                imgs_url = "https://static.geetest.com/" + res["data"]['imgs']
                slide_bytes = requests.get(imgs_url).content
                # new_pic = ImageProcess.mergePic(slide_bytes, bytes_list)
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
                # click_list = []
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

    def re_js_code(self):
        params_list = self.get_1()
        headers = {
            "Host": "static.geetest.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
            "origin": "https://www.tianyancha.com",
            "dnt": "1",
            "sec-ch-ua-mobile": "?0",
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
        matche_03 = re.search(r"!function\(\){var.*?};}\(\),", response.text, re.S)
        text = matche_03.group()
        matche_04 = re.search(r"var.*?};", text, re.S)
        str_code += "function get_param(){" + matche_04.group()
        matche_05 = re.search(r'\{"(.*?)}', text, re.S)
        try:
            str_code1 = str_code + "return " + matche_05.group() + "};}"
            res = execjs.compile(str_code1).call("get_param")
        except:
            try:
                str_code2 = str_code + "return " + matche_05.group() + "}"
                res = execjs.compile(str_code2).call("get_param")
            except:
                str_code3 = str_code + "return " + matche_05.group() + "};"
                res = execjs.compile(str_code3).call("get_param")
        return {"par_param": res, "par_data": params_list}


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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://gcaptcha4.geetest.com/verify"
        res = self.re_js_code()
        logger.info(res)
        with open("w_pass.js", encoding="utf-8") as f:
            jscode = f.read()
        data = execjs.compile(jscode).call("_fff", res["par_data"], res["par_param"])
        params = {
            "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
            "client_type": "web",
            "lot_number": res["par_data"]["lot_number"],
            "payload": res["par_data"]["payload"],
            "process_token": res["par_data"]["process_token"],
            "payload_protocol": "1",
            "pt": "1",
            "w": data["res"]
        }
        response = self.session.get(url, headers=headers, params=params)
        if response.status_code == 200:
            resp = json.loads(str(response.text).strip("(").strip(")"))
            gen_time = resp["data"]["seccode"]["gen_time"]
            captcha_output = resp["data"]["seccode"]["captcha_output"]
            lot_number = resp["data"]["seccode"]["lot_number"]
            pass_token = resp["data"]["seccode"]["pass_token"]
            params_list1 = {
                "lot_number": lot_number,
                "pass_token": pass_token,
                "gen_time": gen_time,
                "captcha_output": captcha_output
            }
            return params_list1
        else:
            logger.error(f"请求状态码:{response.status_code}")


    def get_cookie_csrf(self):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/avif,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Pragma": "no-cache",
            "Referer": "https://www.tianyancha.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.Reqest["ua"],
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                         "Chrome\";v=\"114\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        self.session.get("https://www.tianyancha.com/", headers=headers, proxies=self.Reqest["proxy"])
        self.Reqest["X-TYCID"]=self.session.cookies.get("TYCID")
        headers = {
            'Referer': 'https://www.tianyancha.com/',
        }
        self.session.get('https://hm.baidu.com/hm.js?e92c8d65d92d534b0fc290df538b4758', headers=headers)



    # @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def passVerity(self, sign):
        par = self.get_2()
        with open("verity.js", encoding="utf-8") as f:
            jscode = f.read()
        IfMatch = execjs.compile(jscode).call("verify", par["lot_number"], sign)
        logger.info(IfMatch)
        headers = {
            "Host": "www.tianyancha.com",
            "Cache-Control": "max-age=0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua": self.Reqest["headers"]["sec-ch-ua"],
            "If-Match": f"{IfMatch}",
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
        print(headers)
        url = "https://www.tianyancha.com/sorry/verifyCaptcha4.json"
        data = {
            "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
            "lot_number": par["lot_number"],
            "pass_token": par["pass_token"],
            "gen_time": par["gen_time"],
            "captcha_output": par["captcha_output"],
        }
        data = json.dumps(data, separators=(',', ':'))
        print(self.Reqest["cookies"])
        response = requests.post(url, headers=headers, cookies=self.Reqest["cookies"], data=data)
        if response.status_code == 200:
            if response.json()["state"] == "ok":
                return True
            else:
                logger.error(f"验证失败！响应:{response.json()}")
                raise Exception("验证失败！重试")
                return False
        else:
            logger.error("{}：状态异常！！".format(response.status_code))
            raise Exception("验证失败！重试")
            return False
