# encoding: utf-8
"""
@FileName：simpleLogin.py
@Description：
@Author：18k
@Time：2024/6/4 21:08
@Department：部门
@Website：站点
@Copyright：©2019-2024 职业
:return:
"""


import base64
import hashlib
import io
import json
import os
import random
import re
import time
import uuid
from urllib.parse import quote
import cv2
import execjs
import subprocess
import redis
import requests
from feapder.network.user_agent import get
from loguru import logger
from retrying import retry
import ddddocr

from config import checkconfig
from passVerify.geetest4_word import get_word_position

def proxy_list():
    tunnel = "d152.kdltps.com:15818"
    # 用户名密码方式
    username = "t13206952228334"
    password = "wtx4i2in:%d"%random.randint(1, 5)
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
    }
    # resp = requests.get("https://myip.ipip.net", proxies=proxies)
    # if resp.status_code == 200:
    #     print(resp.text)
    # return proxies
    return None
    # else:
    #     raise Exception("请求代理")


ocr = ddddocr.DdddOcr(det=False, ocr=False)
ocr1 = ddddocr.DdddOcr(beta=True)  # 切换为第二套ocr模型
ocr2 = ddddocr.DdddOcr(det=True)

@retry(wait_fixed=1)
class CC1:
    def PostPic(self,final_image):
        out_buff=io.BytesIO()
        final_image.save(out_buff, format='PNG')
        byte_pic=out_buff.getvalue()
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "DNT": "1",
            "Origin": "http://124.222.86.140:8000",
            "Pragma": "no-cache",
            "Referer": "http://124.222.86.140:8000/char1",
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
            data=response.json()
            _crop=data["data"]["res"]["crop_centre"]
            return _crop
        else:
           raise Exception("链接失效")


class CC2:
    def PostPic(self,pic_list):
        if len(pic_list) == 4:
            pic_list.append("")
        tmp = str(time.time())
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        }
        url = "http://192.168.5.181:10121/geetest4_word/gradio_api/queue/"
        # url = "http://192.168.5.70:10121/geetest4_word/gradio_api/queue/"
        params = {"": ""}
        data = {"data": pic_list,"fn_index": 1,"session_hash": tmp}
        data = json.dumps(data, separators=(',', ':'))
        requests.post(url + "join", headers=headers, params=params, data=data, verify=False)
        params = {"session_hash": tmp}
        response = requests.get(url + "data", headers=headers, params=params, verify=False)
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


class Login_module:

    def __init__(self,mobil):
        self.config = checkconfig("bendi")
        self.local_VQ_conn = redis.Redis("192.168.5." + self.config["uAddr"][0],
                                         self.config["uAddr"][1],
                                         self.config["uAddr"][2],
                                         self.config["uAddr"][3],
                                         socket_connect_timeout=1155)
        self.Reqest = {}
        self.mobil = mobil
        self.session = requests.session()


    def ocr_img(self,img, filepath):
        with open(img, 'rb') as f:
            image = f.read()
        bboxes = ocr2.detection(image)
        # print(bboxes)
        im = cv2.imread(img)
        for bbox in bboxes:
            x1, y1, x2, y2 = bbox
            im = cv2.rectangle(im, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)
        cv2.imwrite(filepath + "/click_img_new.jpg", im)


    def download_img(self,imgs, filename, type, uuid):
        dir_path = f"C:/Users/Administrator/Desktop/imgs/{type}/{uuid}"
        file_path = os.path.join(dir_path, filename + ".png")
        # 如果文件夹不存在则创建
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if type == "slide":
            with open(file_path, 'wb') as f:
                f.write(imgs)
        elif type == "word":
            with open(file_path, 'wb') as f:
                f.write(imgs)
            if filename == "click_img":
                self.ocr_img(file_path, dir_path)

    def get_1(self):
        self.get_cookie_csrf()
        uuid1 = uuid.uuid1()
        headers = {
            "Host": "gcaptcha4.geetest.com",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
            "DNT": "1",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": self.Reqest["ua"],
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
            "challenge": uuid1,
            "client_type": "web",
            "lang": "zho"
        }
        response = self.session.get(url, headers=headers, params=params, proxies=self.Reqest["proxy"])
        if response.status_code == 200:
            cookies = response.cookies.get("captcha_v4_user")
            resp = json.loads(response.text.strip("(").strip(")"))
            # print(resp)
            type = resp["data"]['captcha_type']
            lot_number = resp["data"]["lot_number"]
            process_token =resp["data"]["process_token"]
            pow_detail =resp["data"]["pow_detail"]
            pow_detail = [pow_detail[i] for i in pow_detail if isinstance(pow_detail, dict)]
            payload =resp["data"]["payload"]
            static_path =resp["data"]["static_path"]
            params_list = {
                "lot_number": lot_number,
                "process_token": process_token,
                "pow_detail": pow_detail,
                "payload": payload,
                "cookies": cookies,
                "static_path": static_path
            }
            if type == 'word':
                print(">>>>>>>>>>>>>>>>>>>>>>>>点选>>>>>>>>>>>>>>")
                q_list = resp["data"]['ques']
                # bytes_list=[]
                base_list=[]
                for index, img_url in enumerate(q_list):
                    tag = requests.get("https://static.geetest.com/" + img_url).content
                    base_list.append(tag)
                imgs_url = "https://static.geetest.com/" + resp["data"]['imgs']
                slide_bytes = requests.get(imgs_url).content
                click_list =get_word_position(slide_bytes,base_list)
                click_smark = []
                for _word in click_list:
                    click_smark.append([round(int(_word[0]) * 100 / 3), round(int(_word[1]) * 50)])
                logger.info(click_smark)
                # self.download_img(slide_bytes, "click_img", type, uuid1)
                params_list["smark"] = click_smark
                params_list["type"] = "word"
            elif type == 'slide':
                print(">>>>>>>>>>>>>>>>>>>>>>>>滑块>>>>>>>>>>>>>>")
                slide_url = "https://static.geetest.com/" + resp["data"]['slice']
                bg_url = "https://static.geetest.com/" + resp["data"]['bg']
                target_bytes = requests.get(slide_url).content
                bg_bytes = requests.get(bg_url).content
                dis = ocr.slide_match(target_bytes, bg_bytes, simple_target=True)["target"][0]
                logger.info(dis)
                # self.download_img(bg_bytes, "bg_img", type, uuid1)
                params_list["dis"] = dis
                params_list["type"] = "slide"
            return params_list

    def Composite_parameter(self,lotNumber):
        lot = {
            "$_JP": [
                {
                    "$_JP": [
                        {
                            "$_JP": [
                                2,
                                3
                            ]
                        },
                        {
                            "$_JP": [
                                17,
                                18
                            ]
                        }
                    ]
                },
                {
                    "$_JP": [
                        {
                            "$_JP": [
                                15
                            ]
                        },
                        {
                            "$_JP": [
                                5
                            ]
                        },
                        {
                            "$_JP": [
                                9
                            ]
                        },
                        {
                            "$_JP": [
                                17
                            ]
                        }
                    ]
                },
                {
                    "$_JP": [
                        {
                            "$_JP": [
                                10,
                                15
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
                                1,
                                8
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
        return {res1[0]: {res1[1]: {res1[2]: res2[0]}}}


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
                "User-Agent":self.Reqest["ua"],
                "sec-ch-ua-platform": "\"Windows\"",
                "accept": "*/*",
                "sec-fetch-site": "cross-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "script",
                "referer": "https://www.tianyancha.com/",
                "accept-language": "zh-CN,zh;q=0.9"
                }
        url = "https://static.geetest.com" + params_list["static_path"] + "/js/gcaptcha4.js"
        response = self.session.get(url,headers=headers,proxies=self.Reqest["proxy"])
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
        match = re.search(pattern,text)
        if match:
            matche_05=match.group(0)
        else:
            matche_05 = re.search(r'\{"(.*?)}', text, re.S)
        try:
            str_code1 = str_code + "return " + matche_05 + "};}"
            res = execjs.compile(str_code1).call("get_param")
        except Exception as e:
            logger.error(e)
            try:
                str_code2 = str_code + "return " + matche_05 + "}"
                res = execjs.compile(str_code2).call("get_param")
            except:
                str_code3 = str_code + "return " + matche_05 + "};"
                res = execjs.compile(str_code3).call("get_param")
        return {"par_param":res,"par_data":params_list}


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
                    "User-Agent":self.Reqest["ua"],
                    "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", "
                                 "\"Chromium\";v=\"123\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\""
                    }
            url = "https://gcaptcha4.geetest.com/verify"
            # par = self.re_js_code()
            par = self.get_1()
            par["par_param"]={'pMVM': 'AwII'}
            param = self.Composite_parameter(par["lot_number"])
            jscode = open("w_decode.js", encoding="utf-8",errors="ignore").read()
            data = execjs.compile(jscode).call("_fff",par,par["par_param"],param)
            params = {
                "captcha_id":"517df78b31ff1b8f841cd86fc0db9f3e",
                "client_type": "web",
                "lot_number": par["lot_number"],
                "payload": par["payload"],
                "process_token": par["process_token"],
                "payload_protocol": "1",
                "pt": "1",
                "w": data["res"]
            }
            response = self.session.get(url,
                    headers=headers,
                    params=params,
                    proxies=self.Reqest["proxy"])
            if response.status_code == 200:
                resp = json.loads(str(response.text).strip("(").strip(")"))
                gen_time = resp["data"]["seccode"]["gen_time"]
                captcha_output = resp["data"]["seccode"]["captcha_output"]
                lot_number =resp["data"]["seccode"]["lot_number"]
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

    def get_3(self):
        try:
            data = self.get_2()
            headers = {
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json",
                    "DNT": "1",
                    "Origin": "https://www.tianyancha.com",
                    "Pragma": "no-cache",
                    "Referer": "https://www.tianyancha.com/",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-site",
                    "User-Agent":self.Reqest["ua"],
                    "X-TYCID": self.Reqest["X-TYCID"],
                    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", "
                                 "\"Chromium\";v=\"114\", \"Google "
                                 "Chrome\";v=\"114\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\""
                    }
            url = "https://napi-huawei.tianyancha.com/next/web" \
                  "/cdloginv2_validatev2"
            params = {
                    "mobile": self.mobil["mobil"],
                    "cdpassword": hashlib.md5(
                            self.mobil["pwd"].encode("utf-8")).hexdigest(),  # md5算法
                    "loginway": "PL",
                    "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
                    "lot_number": data["lot_number"],
                    "pass_token": data["pass_token"],
                    "gen_time": data["gen_time"],
                    "captcha_output": data["captcha_output"],
                    "captcha_type": "pcLogin",
                    "autoLogin": False}
            response = self.session.get(url,headers=headers,params=params,proxies=self.Reqest["proxy"])
            response.encoding="utf-8"
            if response.status_code == 200:
                if "输入的手机号码与密码不匹配，推荐使用短信登录" not in response.text:
                    res = json.loads(str(response.text).strip("(").strip(")"))
                    print("登录响应结果----->:",res)
                    if res["message"]=="":
                        token = res["data"]['token']
                        id = str(res["data"]['userId'])
                        js_code = open("signCook.js",encoding="utf-8").read()
                        res = execjs.compile(js_code).call("get_ssion",id)
                        sensorsdata = quote(json.dumps({
                                "distinct_id": id,
                                "first_id": res["device_id"],
                                "props": "{}",
                                "identities": res["identities"],
                                "history_login_id": {
                                        "name": "$identity_login_id",
                                        "value": id
                                        },
                                "$device_id": res["device_id"]}))
                        user_info = quote(json.dumps({
                                "state": "4",
                                "vipManager": "0",
                                "mobile": self.mobil["mobil"],
                                "userId": id,
                                "isExpired": "0"}))
                        self.session.cookies.set("sensorsdata2015jssdkcross",sensorsdata)
                        self.session.cookies.set("tyc-user-info",user_info)
                        self.session.cookies.set("tyc-user-info-save-time",str(int(time.time() * 1000)))
                        self.session.cookies.set("tyc-user-phone","%255B%252218587162714%2522%255D")
                        self.session.cookies.set("auth_token",token)
                        self.session.cookies.set("ssuid",id)
                        logger.success(f"{self.mobil}:登录成功，同学开始愉快的玩耍吧！！")
                        self.Reqest["auth_token"] = token
                        self.get_cookie_csrf()
                        return True
                    elif res["message"]=="账号存在风险，暂不能操作":
                        logger.error("{}:{}".format(self.mobil,response.json()["message"]))
                        self.local_VQ_conn.sadd("ErrorUser",json.dumps(self.mobil))
                        with open("C:/Users/Administrator/Desktop/账号被封.txt", "a", encoding="utf-8") as f:
                            f.write(self.mobil["mobil"] + "密码" + self.mobil["pwd"] + "\n")
                        return False
                    elif "密码登录冻结，请使用验证码登录" in res["message"]:
                        print(res["message"])
                        logger.error("{}:{}".format(self.mobil,"密码登录冻结，请使用验证码登录"))
                        self.local_VQ_conn.sadd("ErrorPwd", json.dumps(self.mobil))
                    else:
                        logger.error(res)
                        return False
                else:
                    logger.error(f"{self.mobil}:账号密码错误!!")
                    with open("C:/Users/Administrator/Desktop/账号密码错误.txt","a",encoding="utf-8")as f:
                            f.write(self.mobil["mobil"]+"密码"+self.mobil["pwd"]+"\n")
                    self.local_VQ_conn.sadd("ErrorPwd", json.dumps(self.mobil))
                    return False
            else:
                logger.error(f"{self.mobil}：账号异常无法登陆!!")
                with open("C:/Users/Administrator/Desktop/账号异常无法登陆.txt","a",encoding="utf-8")as f:
                            f.write(self.mobil["mobil"]+"密码"+self.mobil["pwd"]+"\n")
                return False
        except Exception as e:
            logger.error(e)

    def get_cookie_csrf(self):
        url = "https://www.tianyancha.com/"
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
                "User-Agent":self.Reqest["ua"],
                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                             "Chrome\";v=\"114\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\""}
        self.session.get(url,headers=headers,proxies=self.Reqest["proxy"])
        self.Reqest["X-TYCID"]=self.session.cookies.get("TYCID")
        self.Reqest["CDID"]=self.session.cookies.get("CDID")
        headers = {
            'Referer': 'https://www.tianyancha.com/',
        }
        self.session.get('https://hm.baidu.com/hm.js?e92c8d65d92d534b0fc290df538b4758', headers=headers,proxies=self.Reqest["proxy"])

    def main(self,proxy,ua):
        self.Reqest["proxy"]=proxy
        self.Reqest["ua"]=ua
        if self.get_3():
            return self.session,self.Reqest
        else:
            return False



if __name__ == '__main__':
    proxy=proxy_list()
    ua=get()
    mobil={"mobil": "13699042888", "pwd": "12310000a"}
    result = Login_module(mobil).main(proxy, ua)
