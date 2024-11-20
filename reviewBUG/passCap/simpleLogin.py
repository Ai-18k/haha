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

import sys
import os
import uuid

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)

# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)


import base64
import hashlib
import io
import json
import re
import time
import random
from urllib.parse import quote
import ddddocr
import execjs
import redis
import requests
from loguru import logger
from feapder.network.user_agent import get
# from curl_cffi import requests
from retrying import retry


ocr = ddddocr.DdddOcr(det=False, ocr=False)
ocr1 = ddddocr.DdddOcr(beta=True)  # 切换为第二套ocr模型
ocr2 = ddddocr.DdddOcr(det=True)


class CC1:
    def PostPic(self, img: bytes, codesore: str):
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
        # url = "http://124.222.86.140:8000/api/charDianxuan/identify"
        url = "http://127.0.0.1"
        data = {
            "imageSource": base64.b64encode(img).decode("utf-8"),
            "dataType": 2,
            "input_chars": codesore
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, data=data, verify=False)
        if response.status_code == 200:
            data = response.json()
            _crop = data["data"]["res"]["crop_centre"]
            return _crop
        else:
            return None


class CC2:
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

class LoginModule:

    def __init__(self):
        self.local_conn = redis.Redis(host='127.0.0.1', port=7980, db=0, password="qwe!@#SDF345788",socket_connect_timeout=1170)
        self.session = requests.Session()
        self.finger = ["chrome99", "chrome100", "chrome101", "chrome104", "chrome107",
                       "chrome110", "chrome116", "chrome119", "chrome120", "edge99",
                       "edge101", "safari15_3","safari15_5", "safari17_0", "chrome99"]
        self.Reqest = {}


    def get_1(self):
        try:
            uuid1 = uuid.uuid1()
            self.get_cookie_csrf()
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
                "challenge":uuid1,
                "client_type": "web",
                "lang": "zho"
            }
            response = self.session.get(url, headers=headers, params=params,proxies=self.Reqest["proxy"] )
            if response.status_code == 200:
                cookies = response.cookies.get("captcha_v4_user")
                resp = json.loads(response.text.strip("(").strip(")"))
                type = resp["data"]['captcha_type']
                lot_number = resp["data"]["lot_number"]
                process_token =resp["data"]["process_token"]
                pow_detail = resp["data"]["pow_detail"]
                pow_detail = [pow_detail[i] for i in pow_detail if isinstance(pow_detail, dict)]
                payload = resp["data"]["payload"]
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
                    base_list = []
                    for index, img_url in enumerate(q_list):
                        tag = requests.get("https://static.geetest.com/" + img_url).content
                        word_pic = base64.b64encode(tag).decode("utf-8")
                        base_list.append(word_pic)
                    imgs_url = "https://static.geetest.com/" + resp["data"]['imgs']
                    slide_bytes = requests.get(imgs_url).content
                    new_pic=[base64.b64encode(slide_bytes).decode("utf-8")]+base_list
                    click_list = CC().PostPic(new_pic)
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
                    # self.download_img(target_bytes, "slide_img", type, uuid1)
                    params_list["dis"] = dis
                    params_list["type"] = "slide"
                return params_list
        except Exception as e:
            logger.error(e)


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

    def Composite_parameter(self, lotNumber):
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
        par["par_param"] = {'pMVM': 'AwII'}
        param = self.Composite_parameter(par["lot_number"])
        jscode = open("w_decode.js", encoding="utf-8").read()
        data = execjs.compile(jscode).call("_fff", par, par["par_param"], param)
        params = {
            "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
            "client_type": "web",
            "lot_number": par["lot_number"],
            "payload": par["payload"],
            "process_token": par["process_token"],
            "payload_protocol": "1",
            "pt": "1",
            "w": data["res"]
        }
        response = self.session.get(url,headers=headers,params=params,proxies=self.Reqest["proxy"])
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
                "User-Agent": self.Reqest["ua"],
                "X-TYCID": self.Reqest["X-TYCID"],
                "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", "
                             "\"Chromium\";v=\"123\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\""
            }
            url = "https://napi-huawei.tianyancha.com/next/web/cdloginv2_validatev2"
            logger.info("【R】{}用户正在登录.......".format(self.Reqest["mobil"]))
            params = {
                "mobile": self.Reqest["mobil"]["mobil"],
                "cdpassword": hashlib.md5(self.Reqest["mobil"]["pwd"].encode("utf-8")).hexdigest(),  # md5算法
                "loginway": "PL",
                "captcha_id":"517df78b31ff1b8f841cd86fc0db9f3e",
                "lot_number": data["lot_number"],
                "pass_token": data["pass_token"],
                "gen_time": data["gen_time"],
                "captcha_output": data["captcha_output"],
                "captcha_type": "pcLogin"
            }
            response = self.session.get(url,
                                            headers=headers,
                                            params=params,
                                            proxies=self.Reqest["proxy"])
            if response.status_code == 200:
                res = json.loads(str(response.text).strip("(").strip(")"))
                print(res)
                if res["message"]=="":
                    token = res["data"]['token']
                    id=str(res["data"]['userId'])
                    self.Reqest["userid"]=id
                    self.create_cookie(self.Reqest["mobil"]["mobil"],id)
                    logger.success("登录成功，同学开始愉快的玩耍吧！！")
                    logger.info("【R】{}用户登录已成功！获取的sign：{}".format(id, token))
                    self.session.cookies.set("auth_token", token)
                    self.Reqest["token"] = token
                    self.get_cookie_csrf()
                    return True
                elif res["message"]=="账号存在风险，暂不能操作" or "输入的手机号码与密码不匹配，推荐使用短信登录":
                    self.local_conn.sadd("406Mobil", json.dumps(self.Reqest["mobil"]))
                    self.local_conn.lrem("searchMobil", 1, json.dumps(self.Reqest["mobil"]))
                    mobil = self.local_conn.lpop("searchMobil")
                    self.local_conn.rpush("searchMobil", mobil)
                    self.Reqest["mobil"] = json.loads(mobil)
                    self.get_3()
                else:
                    logger.error(f"登陆异常: {res}")
                    time.sleep(1)
                    self.get_3()
                    return
        except Exception as e:
            logger.error(e)
            self.main(self.Reqest["mobil"])
            return

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
        url = "https://www.tianyancha.com/"
        self.session.get(url, headers=headers, proxies=self.Reqest["proxy"])
        self.Reqest["X-TYCID"]=self.session.cookies.get("TYCID")
        headers = {
            'Referer': 'https://www.tianyancha.com/',
        }
        self.session.get('https://hm.baidu.com/hm.js?e92c8d65d92d534b0fc290df538b4758', headers=headers)

    def create_cookie(self,m,id):
        js_code = open("signCook.js", encoding="utf-8").read()
        res = execjs.compile(js_code).call("get_ssion",id)
        sensorsdata = quote(json.dumps({
            "distinct_id":id,
            "first_id": res["device_id"],
            "props": {},
            "identities": res["identities"],
            "history_login_id": {
                "name": "$identity_login_id",
                "value": id
            },
            "$device_id": res["device_id"]
        }))
        user_info = quote(json.dumps({
            "state": "4",
            "vipManager": "0",
            "mobile": m,
            "userId":id,
            "isExpired": "0"
        }))
        self.session.cookies.set("sensorsdata2015jssdkcross", sensorsdata)
        self.session.cookies.set("tyc-user-info", user_info)
        self.session.cookies.set("tyc-user-info-save-time", str(int(time.time() * 1000)))
        self.session.cookies.set("tyc-user-phone", "%255B%252218587162714%2522%255D")

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
        # resp = requests.get("https://myip.top", proxies=proxies)
        # if resp.status_code == 200:
        #     print(resp.text)
        return proxies
        # return None
        # else:
        #     raise Exception("请求代理")


    def main(self,mobil):
        self.Reqest["proxy"] =self.proxy_list()
        self.Reqest["ua"] = get()
        self.Reqest["mobil"] = mobil
        if self.get_3():
            timestamp = int(time.time() - random.randint(30000, 40000))
            self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758", "{},{},{},{}".
                                     format(str(timestamp - random.randint(30000, 40000)),
                str(timestamp - random.randint(20000, 30000)),
                str(timestamp - random.randint(10000, 20000)),
                str(timestamp)))
            self.Reqest["sessionNo"] = "{:.8f}".format(time.time())
            self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758", str(int(time.time()) - 4000))
            cookie_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
            print("======cookie_dict:", {
                "cookie_dict": cookie_dict,
                "ua": self.Reqest["ua"],
                "token": self.Reqest["token"],
                "sign": self.Reqest["sign"],
                "userid": self.Reqest["userid"],
                "sessionNo": self.Reqest["sessionNo"],
                "mobil": mobil
            })
            cookie_data = {
                "cookie_dict": cookie_dict,
                "ua": self.Reqest["ua"],
                "token": self.Reqest["token"],
                "sign": self.Reqest["sign"],
                "userid": self.Reqest["userid"],
                "sessionNo": self.Reqest["sessionNo"],
                "mobil": mobil
            }
            for i in range(8):
                self.local_conn.lpush("searchCookie", json.dumps(cookie_data))
        else:
            return False


if __name__ == '__main__':
    mobil = {"mobil": "13078754552", "pwd": "cc123456"}
    LoginModule().main(mobil)
