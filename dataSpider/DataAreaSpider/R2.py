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

import math
import uuid
from concurrent.futures import ThreadPoolExecutor
from retrying import retry
from pymongo import MongoClient, WriteConcern
import os
import random
from feapder.network.user_agent import get
import requests
import json
from loguru import logger
import execjs
import hashlib
import time
from urllib.parse import quote
import re
import redis
import ddddocr
import cv2
from passVerify.geetest4_word import get_word_position


ocr = ddddocr.DdddOcr(det=False, ocr=False,show_ad=False)
ocr2 = ddddocr.DdddOcr(det=True,show_ad=False)


def checkconfig():
    with open("../../setting/config.json","r",encoding="utf-8") as file:
        config = file.read()
    config = json.loads(config)
    if 'localSAddr' not in config:
        logger.error("请设置数据保存地址！！")
        raise "未设置文件保存地址"
    else:
        if len(config['localSAddr'])<2:
            logger.error("请 正确配置 数据保存地址！！")
            raise "未正确配文件保存地址"
    if config["rkey"] not in config["fAddr"]:
        logger.error("未找到与之相关的设备信息，请检查名称或者检查设备是否存在")
        raise "名称有误或者设备不存在，请检查！！"

    config["rkey"]="hebei"
    config["rkey"]="hebei"

    return config


class CC:
    def PostPic(self, pic_list):
        if len(pic_list) == 4:
            pic_list.append("")
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


class SuccessCODE():

    def __init__(self):
        self.config=checkconfig()
        self.client = MongoClient("192.168.5."+self.config['localSAddr'][0],
                                  self.config['localSAddr'][1])
        self.client_01 = MongoClient(host="139.9.70."+self.config["servSAddr"][0],
                                     port=self.config["servSAddr"][1],
                                     username=self.config["servSAddr"][2],
                                     password=self.config["servSAddr"][3],
                                     authSource=self.config["servSAddr"][4])
        self.local_VQ_conn = redis.Redis("192.168.5."+self.config["uAddr"][0],
                                         self.config["uAddr"][1],
                                         self.config["uAddr"][2],
                                         self.config["uAddr"][3],
                                         socket_connect_timeout=self.config["uAddr"][4])
        self.local_conn = redis.Redis("192.168.5."+self.config["fAddr"][self.config["rkey"]][0],
                                      self.config["fAddr"][self.config["rkey"]][1],
                                      self.config["fAddr"][self.config["rkey"]][2],
                                      self.config["fAddr"][self.config["rkey"]][3],
                                      socket_connect_timeout=1170)
        self.session = requests.session()
        self.coll = self.client[self.config["rkey"]]["company_id"]
        self.coll_1 = self.client_01[self.config["rkey"]]["company_id"]
        self.s_data = self.client[self.config["rkey"]]["sorcomp"]
        self.Request={}
        self.filter = self.config["rkey"]+":filter:company_id"
        self.filter_params =self.config["rkey"]+":filter:params"
        self.filter_comp = self.config["rkey"]+":filter:comp"
        self.com_id = self.config["rkey"]+":company_id"
        self.params=self.config["rkey"]+":params"
        self.failparam=self.config["rkey"]+":fail_params"
        self.write_concern = WriteConcern(w=1)

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
        dir_path = self.config["imgpath"]+f"/{type}/{uuid}"
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
                "User-Agent": self.Request["ua"],
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
            response = self.session.get(url, headers=headers, params=params,proxies=self.Request["proxy"])
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
                        # word_pic = base64.b64encode(tag).decode("utf-8")
                        # base_list.append(word_pic)
                        base_list.append(tag)
                    imgs_url = "https://static.geetest.com/" + resp["data"]['imgs']
                    slide_bytes = requests.get(imgs_url).content
                    # new_pic=[base64.b64encode(slide_bytes).decode("utf-8")]+base_list
                    # click_list = CC().PostPic(new_pic)
                    click_list = get_word_position(slide_bytes,base_list)
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
            "User-Agent": self.Request["ua"],
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


    @retry(stop_max_attempt_number=5, wait_fixed=1000)
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
            "User-Agent": self.Request["ua"],
            "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", "
                         "\"Chromium\";v=\"123\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://gcaptcha4.geetest.com/verify"
        par = self.get_1()
        par["par_param"] = {'rw0k': 'cpej'}
        param = self.Composite_parameter(par["lot_number"])
        jscode = open("../../RiskcontrolPass/jscode/w_decode.js", encoding="utf-8").read()
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
        response = self.session.get(url,headers=headers,params=params,proxies=self.Request["proxy"],timeout=10)
        if response.status_code == 200:
            resp = json.loads(str(response.text).strip("(").strip(")"))
            gen_time = resp["data"]["seccode"]["gen_time"]
            captcha_output = resp["data"]["seccode"]["captcha_output"]
            lot_number = resp["data"]["seccode"]["lot_number"]
            pass_token = resp["data"]["seccode"]["pass_token"]
            self.Request["sign"] = data["pow_sign"]
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
                "User-Agent": self.Request["ua"],
                "X-TYCID": self.Request["X-TYCID"],
                "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", "
                             "\"Chromium\";v=\"123\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\""
            }
            url = "https://napi-huawei.tianyancha.com/next/web/cdloginv2_validatev2"
            logger.info("【R】{}用户正在登录.......".format(self.Request["mobil"]))
            params = {
                "mobile": self.Request["mobil"]["mobil"],
                "cdpassword": hashlib.md5(self.Request["mobil"]["pwd"].encode("utf-8")).hexdigest(),  # md5算法
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
                                            proxies=self.Request["proxy"])
            if response.status_code == 200:
                res = json.loads(str(response.text).strip("(").strip(")"))
                print(res)
                if res["message"]=="":
                    token = res["data"]['token']
                    id=str(res["data"]['userId'])
                    self.Request["userid"]=id
                    self.create_cookie(self.Request["mobil"]["mobil"],id)
                    logger.success("登录成功，同学开始愉快的玩耍吧！！")
                    logger.info("【R】{}用户登录已成功！获取的sign：{}".format(id, token))
                    self.session.cookies.set("auth_token", token)
                    self.Request["token"] = token
                    self.get_cookie_csrf()
                elif res["message"]=="账号存在风险，暂不能操作" or "输入的手机号码与密码不匹配，推荐使用短信登录":
                    self.local_VQ_conn.sadd("ErrorMobil", json.dumps(self.Request["mobil"]))
                    self.local_VQ_conn.lrem("searchMobil", 1, json.dumps(self.Request["mobil"]))
                    mobil = self.local_VQ_conn.lpop("searchMobil")
                    self.local_VQ_conn.rpush("searchMobil", mobil)
                    self.Request["mobil"] = json.loads(mobil)
                    self.get_3()
                else:
                    logger.error(f"登陆异常: {res}")
                    time.sleep(1)
                    self.get_3()
                    return
        except Exception as e:
            logger.error(e)
            self.main()
            return


    @retry(stop_max_attempt_number=5, wait_fixed=1000)
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
            "User-Agent": self.Request["ua"],
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                         "Chrome\";v=\"114\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://www.tianyancha.com/"
        self.session.get(url, headers=headers, proxies=self.Request["proxy"],timeout=10)
        self.Request["X-TYCID"]=self.session.cookies.get("TYCID")
        headers = {
            'Referer': 'https://www.tianyancha.com/',
        }
        self.session.get('https://hm.baidu.com/hm.js?e92c8d65d92d534b0fc290df538b4758',
                         headers=headers,proxies=self.Request["proxy"],timeout=10)

    def create_cookie(self,m,id):
        js_code = open("../../RiskcontrolPass/jscode/signCook.js", encoding="utf-8").read()
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
        global l
        l = random.randint(1, 8)
        # 隧道域名:端口号
        tunnel = self.config["proxy"]["tunnel"]
        # 用户名密码方式
        username = self.config["proxy"]["username"]
        password = "%s:%d" % (self.config["proxy"]["pwd"],l)
        proxies = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
        }
        try:
            resp = requests.get("https://myip.ipip.net", proxies=proxies)
            if resp.status_code == 200:
                print(resp.text)
                return proxies
            else:
                return None
        except Exception as e:
            logger.error(e)
            return None


    def paramdata(self):


    def next_page(self,info,page):
        while True:
            try:
                self.session.headers.update({
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/json",
                    "version": "TYC-Web",
                    "eventId": "i246",
                    "pm": "451",
                    "spm": "i246",
                    "page_id": "SearchResult",
                    "X-TYCID": self.Request["X-TYCID"],
                    "X-AUTH-TOKEN": self.Request["token"]
                })
                url = "https://capi.tianyancha.com/cloud-tempest/company/advance"
                params = {
                    "_": str(int(time.time() * 1000))
                }
                data = {
                    "filterJson": "{\"searchMethod\":{\"key\":\"searchMethod\",\"items\":[{\"value\":\"1\"}]},"
                                  "\"institutionTypeMethod\":{\"key\":\"institutionTypeMethod\",\"items\":[{\"value\":\"0\"}]},"
                                  "\"incomeReportYear\":{\"key\":\"incomeReportYear\",\"items\":[{\"value\":\"最新\"}]},"
                                  "\"incomeReportPeriod\":{\"key\":\"incomeReportPeriod\",\"items\":[{\"value\":\"12\"}]},"
                                  "\"incomeRelation\":{\"key\":\"incomeRelation\",\"items\":[{\"value\":\"gt\"}]},"
                                  "\"economicTypeMethod\":{\"key\":\"economicTypeMethod\",\"items\":[{\"value\":\"0\"}]},"
                                  "\"technologyTypeNewMethod\":{\"key\":\"technologyTypeNewMethod\",\"items\":[{\"value\":\"1\"}]},"
                                  "\"enterTopListMethod\":{\"key\":\"enterTopListMethod\",\"items\":[{\"value\":\"1\"}]},"
                                  "\"certificateTypeMethod\":{\"key\":\"certificateTypeMethod\",\"items\":[{\"value\":\"1\"}]},"
                                  "\"incomeUnit\":{\"key\":\"incomeUnit\",\"items\":[{\"value\":\"万\"}]},\"sortType\":{\"key\":\"sortType\","
                                  "\"items\":[{\"value\":\"0\"}]},\"profitUnit\":{\"key\":\"profitUnit\",\"items\":[{\"value\":\"万\"}]},"
                                  "\"profitRelation\":{\"key\":\"profitRelation\",\"items\":[{\"value\":\"gt\"}]},"
                                  "\"profitReportYear\":{\"key\":\"profitReportYear\",\"items\":[{\"value\":\"最新\"}]},"
                                  "\"profitReportPeriod\":{\"key\":\"profitReportPeriod\",\"items\":[{\"value\":\"12\"}]},"
                                  "\"assetUnit\":{\"key\":\"assetUnit\",\"items\":[{\"value\":\"万\"}]},"
                                  "\"assetRelation\":{\"key\":\"assetRelation\",\"items\":[{\"value\":\"gt\"}]},"
                                  "\"assetReportYear\":{\"key\":\"assetReportYear\",\"items\":[{\"value\":\"最新\"}]},"
                                  "\"assetReportPeriod\":{\"key\":\"assetReportPeriod\",\"items\":[{\"value\":\"12\"}]},"
                                  "\"liabilityUnit\":{\"key\":\"liabilityUnit\",\"items\":[{\"value\":\"万\"}]},"
                                  "\"liabilityRelation\":{\"key\":\"liabilityRelation\",\"items\":[{\"value\":\"gt\"}]},"
                                  "\"liabilityReportYear\":{\"key\":\"liabilityReportYear\",\"items\":[{\"value\":\"最新\"}]},"
                                  "\"liabilityReportPeriod\":{\"key\":\"liabilityReportPeriod\",\"items\":[{\"value\":\"12\"}]},"
                                  "\"financialDataMethod\":{\"key\":\"financialDataMethod\",\"items\":[{\"value\":\"1\"}]},"
                                  "\"areaCode\":{\"key\":\"areaCode\",\"items\":[{\"value\":%s}]},"
                                  "\"institutionType\":{\"key\":\"institutionType\",\"items\":[{\"value\":\"企业\","
                                  "\"childList\":[{\"value\":\"全民所有制\"},{\"value\":\"集体所有制\"},{\"value\":\"联营企业\"}]},"
                                  "{\"value\":\"个体工商户\"},{\"value\":\"农民专业合作社\"},{\"value\":\"事业单位\"},{\"value\":\"学校\"}]},"
                                  "\"establishTimeRange\":{\"key\":\"establishTimeRange\",\"items\":[{\"value\":%s},"
                                  "{\"value\":%s}]}}"%(info["areaCode"],info["new_day"],info["next_day"]),
                    "searchType": 1,
                    "pageNum": page,
                    "pageSize": 20,
                    "eventId": "i244"
                }
                str_data = json.dumps(data, separators=(',', ':'))
                response = self.session.post(url,params=params,data=str_data,proxies=self.Request["proxy"])
                logger.info(info)
                logger.info(self.Request["mobil"])
                logger.info(response.status_code)
                if response.status_code == 200:
                    if response.json()["message"] =="":
                        if "data" in response.json() and "items" in response.json()["data"]:
                            num=math.ceil(response.json()["data"]["resultCount"] / 20) if response.json()["data"]["resultCount"] else 0
                            logger.info(f'这个链接共{num}页数据')
                            logger.info(f'当前是第{page}页')
                            if page > num:
                                break
                            compList = response.json()["data"]["items"]
                            info_list=[]
                            item_list=[]
                            for item in compList:
                                if self.local_conn.sadd(self.filter_comp, item["name"]):
                                    item["areaCode"]=info["areaCode"]
                                    item["city"]=info["city"]
                                    if "_id" in item:
                                        del item["_id"]
                                    item_list.append(item)
                                res = self.local_conn.sadd(self.filter, item["name"])
                                if res:
                                    info.update({"company": item["name"], "id": item["gid"]})
                                    if "_id" in info:
                                        del info["_id"]
                                    self.local_conn.lpush(self.com_id, json.dumps(info))
                                    info_list.append(info)
                                    logger.success(info)
                                else:
                                    logger.warning("【*】已过滤:{}".format({"company": item["name"], "id": item["gid"]}))
                            if item_list:
                                try:
                                    self.s_data.with_options(write_concern=self.write_concern).insert_many(item_list,ordered=False)
                                    logger.success("【*】items-------------保存成功！！")
                                    item_list.clear()
                                except Exception as e:
                                    logger.error(e)
                            if info_list:
                                    try:
                                        self.coll.with_options(write_concern=self.write_concern).insert_many(info_list,ordered=False)
                                        logger.success("【*1】info-------------保存成功！！")
                                    except Exception as e:
                                        logger.error(e)
                                    try:
                                        self.coll_1.with_options(write_concern=self.write_concern).insert_many(info_list,ordered=False)
                                        logger.success("【*2】info-------------保存成功！！")
                                    except Exception as e:
                                        logger.error(e)
                                    info_list.clear()
                            if len(compList) % 20 != 0:
                                logger.info("无数据:{}".format(len(compList)))
                                break
                        else:
                            logger.info(response.text)
                            print("1>>>>>>>>>>>>>>>>>%s" % response.text)
                            mobil = self.local_VQ_conn.lpop("searchMobil")
                            self.local_VQ_conn.rpush("searchMobil", mobil)
                            self.Request["mobil"] = json.loads(mobil)
                            self.Request["ua"] = get()
                            self.Request["proxy"] = self.proxy_list()
                            self.get_3()
                            timestamp = int(time.time() - random.randint(30000, 40000))
                            self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758",
                                                     "{},{},{},{}".format(
                                                         str(timestamp - random.randint(20000, 30000)),
                                                         str(timestamp - random.randint(10000, 20000)),
                                                         str(timestamp - random.randint(5000, 10000)),
                                                         str(timestamp)))
                            self.Request["sessionNo"] = "{:.8f}".format(time.time())
                            self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758",
                                                     str(int(time.time())))
                            self.next_page(info, page)
                            break
                    elif response.json()["message"] =="mustlogin":
                        print("2 >>>>>>>>>>>>>", response.text)
                        self.get_3()
                        timestamp = int(time.time() - random.randint(50000, 60000))
                        self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758",
                                                 "{},{},{},{}".format(
                                                     str(timestamp - random.randint(30000, 40000)),
                                                     str(timestamp - random.randint(20000, 30000)),
                                                     str(timestamp - random.randint(10000, 20000)),
                                                     str(timestamp)))
                        self.Request["sessionNo"] = "{:.8f}".format(time.time())
                        self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758",
                                                 str(int(time.time())))
                        # raise Exception(f"HTTP status code {response.status_code} received.")
                        self.next_page(info, page)
                        break
                    elif response.json()["message"] == '账号存在风险，暂不能操作':
                        print("3 >>>>>>>>>>>>>", response.text)
                        self.local_VQ_conn.sadd("ErrorMobil", json.dumps(self.Request["mobil"]))
                        print(">>>>>>>>>>>>>>>>>>>>")
                        self.local_VQ_conn.lrem("searchMobil", 1, json.dumps(self.Request["mobil"]))
                        mobil = self.local_VQ_conn.lpop("searchMobil")
                        self.local_VQ_conn.rpush("searchMobil", mobil)
                        self.Request["mobil"] = json.loads(mobil)
                        self.Request["ua"] = get()
                        self.Request["proxy"] = self.proxy_list()
                        self.get_3()
                        timestamp = int(time.time() - random.randint(30000, 40000))
                        self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758",
                                                 "{},{},{},{}".format(
                                                     str(timestamp - random.randint(20000, 30000)),
                                                     str(timestamp - random.randint(10000, 20000)),
                                                     str(timestamp - random.randint(5000, 10000)),
                                                     str(timestamp)))
                        self.Request["sessionNo"] = "{:.8f}".format(time.time())
                        self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758",
                                                 str(int(time.time())))
                        self.next_page(info, page)
                        break
                    elif response.json()["message"]=="您的操作过于频繁, 请稍后重试":
                        print("4>>>>>>>>>>>>>>>>>%s"%response.text)
                        time.sleep(20)
                        self.next_page(info,page)
                        break
                else:
                    print("有风控?")
                page+=1
            except Exception as e:
                logger.error(e)
                if "_id" in info:
                    del info["_id"]
                self.local_conn.lpush(self.failparam,json.dumps(info))


    def main(self):
        theadnum=1
        if self.config["isthread"]["isthread"]:
            theadnum=self.config["isthread"]["num"]
        with ThreadPoolExecutor(theadnum) as f:
            self.Request["ua"] = get()
            self.Request["proxy"] = self.proxy_list()
            mobil = self.local_VQ_conn.lpop("searchMobil")
            self.local_VQ_conn.rpush("searchMobil", mobil)
            self.Request["mobil"] = json.loads(mobil)
            self.get_3()
            timestamp = int(time.time() - random.randint(30000, 40000))
            self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758","{},{},{},{}".
                                     format(str(timestamp - random.randint(20000, 30000)),
                                            str(timestamp - random.randint(10000, 20000)),
                                            str(timestamp - random.randint(5000, 10000)),
                                            str(timestamp)))
            self.Request["sessionNo"] = "{:.8f}".format(time.time())
            self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758",str(int(time.time())))
            _=1
            futures=[]
            while True:
                try:
                    if _ % 300==0:
                        self.Request["ua"]=get()
                        self.Request["proxy"]=self.proxy_list()
                        mobil = self.local_VQ_conn.lpop("searchMobil")
                        self.local_VQ_conn.rpush("searchMobil", mobil)
                        self.Request["mobil"] = json.loads(mobil)
                        self.get_3()
                        timestamp = int(time.time() - random.randint(30000,40000))
                        self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758", "{},{},{},{}".
                                                 format(str(timestamp - random.randint(20000, 30000)),
                                                        str(timestamp - random.randint(10000, 20000)),
                                                        str(timestamp - random.randint(5000, 10000)),
                                                        str(timestamp)))
                        self.Request["sessionNo"] = "{:.8f}".format(time.time())
                        self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758", str(int(time.time())))
                    res = self.local_conn.lpop(self.params)
                    if res is None:
                        logger.success("已全部采集完成!!")
                        break
                    info=json.loads(res.decode("utf-8"))
                    if "company" not in info:
                        info_str = info["areaCode"]+info["base"]+str(info["new_day"])+str(info["next_day"])
                        if self.local_conn.sadd(self.filter_params, info_str):
                            if self.config["isthread"]["isthread"]:
                                futures.append(f.submit(self.next_page,info=info,page=1))
                            else:
                                self.next_page(info,1)
                            _ += 1
                        else:
                            logger.warning(f"【*】参数已经存在:{info}")
                    else:
                        logger.warning("{}:存在company_id".format(info))
                    if self.config["isthread"]["isthread"]:
                        if len(futures)>=20:
                            for future in futures:
                                try:
                                    future.result()
                                except Exception as e:
                                    logger.error(e)
                                    time.sleep(1)
                                    future.result()
                            futures.clear()
                    logger.info(f"。。。。。。。。。。。。这是第 {_} 家公司")
                except redis.exceptions.TimeoutError as e:
                    logger.error(e)
                    self.main()
                    return
            if self.config["isthread"]["isthread"]:
                for future in futures:
                    try:
                        future.result()
                    except:
                        logger.error(e)
                        time.sleep(1)
                        future.result()


if __name__ == '__main__':
    sc = SuccessCODE()
    sc.main()



