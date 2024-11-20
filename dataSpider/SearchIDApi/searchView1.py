#!/usr/bin/env python
#coding=utf-8

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
import base64
import os
import random
import uuid
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import cv2
import ddddocr
import pymongo
from PIL import Image
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
from lxml import etree
from retrying import retry


ocr = ddddocr.DdddOcr(det=False, ocr=False)
ocr1 = ddddocr.DdddOcr(beta=True)  # 切换为第二套ocr模型
ocr2 = ddddocr.DdddOcr(det=True)


class CC:
    def PostPic(self,img:bytes,codesore:str):
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
            "imageSource": base64.b64encode(img).decode("utf-8"),
            "dataType": 2,
            "input_chars": codesore
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, data=data, verify=False)
        if response.status_code == 200:
            data=response.json()
            _crop=data["data"]["res"]["crop_centre"]
            return _crop
        else:
            return None


class SuccessCODE():

    def __init__(self):
        self.local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",
                                      socket_connect_timeout=170)
        self.local_VQ_conn = redis.Redis(host='192.168.5.181', port=7933, db=0, password="fer@nhaweif576KUG",
                                         socket_connect_timeout=1170)
        self.localconn = redis.Redis(host='127.0.0.1.txt', port=7980, db=0, password="qwe!@#SDF345788",
                                      socket_connect_timeout=1170)
        self.conn = redis.Redis(host='139.9.70.234', port=6379, db=6, password="anbo123",socket_connect_timeout=2000)
        self.session = requests.session()
        self.Request={}
        self.client = pymongo.MongoClient(host='192.168.5.167', port=27017)
        self.client_01 = pymongo.MongoClient(host='139.9.70.234', port=12700, username="root",
                                             password="QuyHlxXhW2PSHTwT",
                                             authSource="admin")
        self.coll_2 = self.client_01["guangdong"]["add_company_id"]
        self.coll = self.client["guangdong"]["add_company_id"]

        #设置取值的键值名称
        # self.flag="fujian:sfaj:company"
        self.flag="补id:fail_网络异常"

        #设置临时的过滤键值，用完就删除
        self.filter="filter:临时id过滤"
        self.all_filter="补id:test"

        # 公司id存放位置
        self.lp_redis="补id:add_ID"

        #筛选出的格式有问题的名称，存放redis的位置
        self.error_company_name = "error_data:company_id"

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
        try:
            headers = {
                "Host": "gcaptcha4.geetest.com",
                "Pragma": "no-cache",
                "Cache-Control": "no-cache",
                "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
                "DNT": "1.txt",
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
                "challenge": "09d9c310-e098-467a-8b6c-c61ae6642e3c",
                "client_type": "web",
                "lang": "zho"
            }
            response = self.session.get(url,headers=headers,params=params,proxies=self.Request["proxy"])
            if response.status_code == 200:
                cookies = response.cookies.get("captcha_v4_user")
                res = json.loads(response.text.strip("(").strip(")"))
                type=res["data"]['captcha_type']
                lot_number = res.get("data").get("lot_number")
                process_token = res.get("data").get("process_token")
                pow_detail = res.get("data").get("pow_detail")
                pow_detail =[pow_detail[i] for i in pow_detail if isinstance(pow_detail, dict)]
                payload = res.get("data").get("payload")
                static_path = res.get("data").get("static_path")
                params_list = {
                    "captcha_id":  "517df78b31ff1b8f841cd86fc0db9f3e",
                    "lot_number": lot_number,
                    "process_token": process_token,
                    "pow_detail": pow_detail,
                    "payload": payload,
                    "cookies": cookies,
                    "static_path": static_path
                }
                uuid1 = uuid.uuid1()
                if type == 'word':
                    print(">>>>>>>>>>>>>>>>>>>>>>>>点选>>>>>>>>>>>>>>")
                    q_list = res["data"]['ques']
                    word_list=[]
                    for index,img_url in enumerate(q_list):
                        tag = requests.get("https://static.geetest.com/" + img_url).content
                        # self.download_img(tag,str(index), type, uuid1)
                        tag = Image.open(BytesIO(tag))
                        white_bg = Image.new("RGBA", tag.size, (255, 255, 255, 255))
                        white_bg.paste(tag, (0, 0), tag)
                        result = ocr1.classification(white_bg, png_fix=True)
                        word_list.append(result)
                    logger.info(word_list)
                    imgs_url = "https://static.geetest.com/" + res["data"]['imgs']
                    print(imgs_url)
                    slide_bytes = requests.get(imgs_url).content
                    # res = CC1().PostPic(slide_bytes, "9501")
                    # click_smark = list()
                    # for _word in word_list:
                    #     word_dict = {}
                    #     for index, item in enumerate(res["pic_str"].split('|')):
                    #         word, x, y = item.split(',')
                    #         word_dict[word] = [round(int(x) * 100 / 3), round(int(y) * 50)]
                    #     try:
                    #         """存在ddddocr和超级🦅识别不同"""
                    #         # logger.info(word_dict)
                    #         click_smark.append(word_dict[_word])
                    #     except Exception as e:
                    #         logger.error(e)
                    # logger.info(click_smark)
                    word_str = "".join(i for i in word_list)
                    click_list = CC().PostPic(slide_bytes, word_str)
                    click_smark = []
                    for _word in click_list:
                        click_smark.append([round(int(_word[0])*100/3), round(int(_word[1])*50)])
                    logger.info(click_smark)

                    # self.download_img(slide_bytes, "click_img", type, uuid1)
                    params_list["smark"] = click_smark
                    params_list["type"] = "word"
                elif type == 'slide':
                    print(">>>>>>>>>>>>>>>>>>>>>>>>滑块>>>>>>>>>>>>>>")
                    slide_url = "https://static.geetest.com/" + res["data"]['slice']
                    bg_url = "https://static.geetest.com/" + res["data"]['bg']
                    target_bytes = requests.get(slide_url).content
                    bg_bytes = requests.get(bg_url).content
                    dis = ocr.slide_match(target_bytes,bg_bytes, simple_target=True)["target"][0]
                    # self.download_img(bg_bytes, "bg_img", type, uuid1)
                    # self.download_img(target_bytes, "slide_img", type, uuid1)
                    params_list["dis"]=dis
                    params_list["type"]="slide"
                return params_list
        except Exception as e:
            logger.error(e)



    def re_js_code(self):
            # proxy = cls.proxy_list()
            # UserAgent = get("chrome")
            params_list=self.get_1()
            headers = {
                    "Host": "static.geetest.com",
                    "pragma": "no-cache",
                    "cache-control": "no-cache",
                    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                                 "Chrome\";v=\"114\"",
                    "origin": "https://www.tianyancha.com",
                    "dnt": "1.txt",
                    "sec-ch-ua-mobile": "?0",
                    "user-agent": self.Request["ua"],
                    "sec-ch-ua-platform": "\"Windows\"",
                    "accept": "*/*",
                    "sec-fetch-site": "cross-site",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-dest": "script",
                    "referer": "https://www.tianyancha.com/",
                    "accept-language": "zh-CN,zh;q=0.9"
                    }
            url = "https://static.geetest.com"+params_list["static_path"]+"/js/gcaptcha4.js"
            logger.info(">>>>>>>正在解析js............................")
            response = self.session.get(url,headers=headers,proxies=self.Request["proxy"])
            str_code = ""
            match = re.search(r'(.*?)\.',response.text)
            head = match.group().strip(".")
            # 用正则表达式匹配  找到gyMNB.****}();  前两个函数内容
            matche_01 = re.findall(rf"{head}\..*?\}}\(\);",response.text)
            str_code += matche_01[0] + matche_01[1]
            matche_02 = re.findall(rf'{head}\..*?}};',response.text)
            str_code += matche_02[2] + matche_02[3] + f"function {head}() {{}};"
            # 找到自执行函数
            matche_03 = re.search(r"!function\(\){var.*?};}\(\)",response.text)
            text = matche_03.group()
            # 找到还原方法
            matche_04 = re.search(r"var.*?];",text)
            str_code += "function get_param(){" + matche_04.group()
            # 找到参数列表
            matche_05 = re.search(r'\{".*?\)}',text)
            str_code += "return " + matche_05.group() + "};"
            res = execjs.compile(str_code).call("get_param")
            return {"par_param":res,"par_data":params_list}



    @retry(wait_fixed=2)
    def get_2(self,flag):
        try:
            headers = {
                    "Accept": "*/*",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "DNT": "1.txt",
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
            res=self.re_js_code()
            logger.info(f">>>>>>>>>>>>>>>>>>>>>>>>文件解析完成>>>>>>>>>>>>>>>>>>>>>>")
            if flag == 1:
                jscode = open("../../RiskcontrolPass/jscode/w_decode.js", encoding="utf-8").read()
                data = execjs.compile(jscode).call("_fff", res["par_data"], res["par_param"])
            else:
                jscode = open("../../RiskcontrolPass/jscode/w_decode.js/w_decode_1.js", encoding="utf-8").read()
                data = execjs.compile(jscode).call("_fff_a", res["par_data"])
            params = {
                "captcha_id": res["par_data"]["captcha_id"],
                "client_type": "web",
                "lot_number": res["par_data"]["lot_number"],
                "payload": res["par_data"]["payload"],
                "process_token": res["par_data"]["process_token"],
                "payload_protocol": "1.txt",
                "pt": "1.txt",
                "w": data["res"]
            }
            response = self.session.get(url,
                    headers=headers,
                    params=params,
                    proxies=self.Request["proxy"])
            if response.status_code == 200:
                res = json.loads(str(response.text).strip("(").strip(")"))
                if res["data"]["result"]=='continue':
                    par = self.re_js_code()
                    js_code_1 = open("../../RiskcontrolPass/jscode/R.config", encoding="utf-8").read()
                    js_code='''
                    function _fff_a(aa) {
            var $_CAGHi = NXVNj.$_Ci,
            $_CAGGR = ['$_CAHAO'].concat($_CAGHi),
            $_CAGIm = $_CAGGR[1.txt];
            function nn(e, t, s, n, i, r, o) {
                console.log(e,t,s,n,i,r,o);
                var $_HADCk = NXVNj.$_Dj()[0][10];
                for (; $_HADCk !== NXVNj.$_Dj()[6][8];) {
                    switch ($_HADCk) {
                        case NXVNj.$_Dj()[3][10]:
                            var a = i % 4,
                                _ = parseInt(i / 4, 10),
                                u = function g(e, t) {
                                    var $_CAHHY = NXVNj.$_Ci,
                                        $_CAHGO = ['$_CAIAf'].concat($_CAHHY),
                                        $_CAHIR = $_CAHGO[1.txt];
                                    $_CAHGO.shift();
                                    var $_CAHJk = $_CAHGO[0];
                                    return new Array(t + 1.txt)[$_CAHHY(134)](e);
                                }($_CAGHi(152), _),
                                c = n + $_CAGIm(175) + i + $_CAGIm(175) + s + $_CAGIm(175) + r + $_CAGHi(175) + t + $_CAGHi(175) + e + $_CAGIm(175) + o + $_CAGIm(175);
                            $_HADCk = NXVNj.$_Dj()[0][9];
                                var h = key,
                                    p = c + h,
                                    l = CryptoJS.MD5(p).toString();
                                return {
                                        "pow_msg": c + h,
                                        "pow_sign": l
                                    };
                    }
                }
            }
            sid=nn(aa.lot_number, aa.captcha_id, aa.pow_detail[3], aa.pow_detail[0], aa.pow_detail[1.txt],aa.pow_detail[2], "")
            var text={
                    "device_id": "",
                    "lot_number": aa.lot_number,
                    "pow_msg": sid.pow_msg,
                    "pow_sign": sid.pow_sign,
                    "geetest": "captcha",
                    "lang": "zh",
                    "ep": "123",
                    "biht": "1426265548",'''+f'"{list(par)[0]}":"{par[list(par)[0]]}",'+\
                    '''
                    "em": {
                        "ph": 0,
                        "cp": 0,
                        "ek": "11",
                        "wd": 1.txt,
                        "nt": 0,
                        "si": 0,
                        "sc": 0
                    }
            }
            _n={
                options:{"pt": "1.txt"}
            }
            res=yl(2).default(JSON.stringify(text),_n);
            return {"res":res,"pow_sign":sid.pow_sign}
        }
        '''
                    with open("../../RiskcontrolPass/jscode/w_decode_1.js", "w", encoding="utf-8") as f:
                        f.write(js_code_1+js_code)
                    self.Request["proxy"]=self.proxy_list()
                    raise Exception("风控")
                gen_time = res.get("data").get("seccode")["gen_time"]
                captcha_output = res.get("data").get("seccode")["captcha_output"]
                captcha_id = res.get("data").get("seccode")["captcha_id"]
                lot_number = res.get("data").get("seccode")["lot_number"]
                pass_token = res.get("data").get("seccode")["pass_token"]
                self.Request["X-TYCID"]=data["pow_sign"]
                params_list1 = {
                        "captcha_id": captcha_id,
                        "lot_number": lot_number,
                        "pass_token": pass_token,
                        "gen_time": gen_time,
                        "captcha_output": captcha_output,
                        "pow_sign": data["pow_sign"],
                        }
                return params_list1
        except Exception as e:
            logger.info(e)



    def get_3(self):
        try:
            data = self.get_2(1)
            headers = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "DNT": "1.txt",
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
                "captcha_id": data["captcha_id"],
                "lot_number": data["lot_number"],
                "pass_token": data["pass_token"],
                "gen_time": data["gen_time"],
                "captcha_output": data["captcha_output"],
                "captcha_type": "pcLogin"
            }
            try:
                response = self.session.get(url,
                                            headers=headers,
                                            params=params,
                                            proxies=self.Request["proxy"])
            except:
                response = self.session.get(url,
                                            headers=headers,
                                            params=params,
                                            proxies=self.Request["proxy"])
            if response.status_code == 200:
                res = json.loads(str(response.text).strip("(").strip(")"))
                print(res)
                if res["message"]=="":
                    token = res["data"]['token']
                    id = str(res["data"]['userId'])
                    self.create_cookie(id, self.Request["mobil"]["mobil"])
                    logger.success("登录成功，同学开始愉快的玩耍吧！！")
                    logger.info("【R】{}用户登录已成功！获取的sign：{}".format(id, token))
                    return token, data["pow_sign"]
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



    def get_cookie_csrf(self):
        try:
            token, sign = self.get_3()
        except Exception as e:
            logger.error(e)
            token, sign = self.get_3()
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                      "image/avif,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1.txt",
            "Pragma": "no-cache",
            "Referer": "https://www.tianyancha.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1.txt",
            "Upgrade-Insecure-Requests": "1.txt",
            "User-Agent": self.Request["ua"],
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                         "Chrome\";v=\"114\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        self.session.cookies.set("auth_token", token)
        url = "https://www.tianyancha.com/"
        self.session.get(url, headers=headers, proxies=self.Request["proxy"])
        self.Request["token"] = token
        self.Request["sign"] = sign

    def create_cookie(self, id, m):
        js_code = open("../../RiskcontrolPass/jscode/signCook.js", encoding="utf-8").read()
        res = execjs.compile(js_code).call("get_ssion", id)
        sensorsdata = quote(json.dumps({
            "distinct_id": id,
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
            "userId": id,
            "isExpired": "0"
        }))
        self.session.cookies.set("sensorsdata2015jssdkcross", sensorsdata)
        self.session.cookies.set("tyc-user-info", user_info)
        self.session.cookies.set("tyc-user-info-save-time", str(int(time.time() * 1000)))
        # self.session.cookies.set("tyc-user-phone", "%255B%252218507051471%2522%252C%2522155%25207958%25204726%2522%252C%2522176%25202167%25204783%2522%255D")
        self.session.cookies.set("tyc-user-phone", "%255B%252218587162714%2522%255D")



    @retry(wait_fixed=2)
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
        # return proxies
        return None
        # else:
        #     raise Exception("请求代理")


    def is_VIP(self):
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://www.tianyancha.com",
            "Pragma": "no-cache",
            "Referer": "https://www.tianyancha.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": self.Request["ua"],
            "X-AUTH-TOKEN": self.Request["token"],
            "X-TYCID": self.Request["sign"],
            "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://napi-huawei.tianyancha.com/next/web/getUserInfo"
        params = {
            "_": str(int(time.time() * 1000))
        }
        response = self.session.get(url, headers=headers, params=params)
        print(response.text)
        if response.status_code == 200:
            if "isVip" in response.json()["data"]:
                logger.success("【*】会员用户:{}!!".format(self.Request["mobil"]))
                return True
            else:
                self.local_VQ_conn.sadd("noMemery", json.dumps(self.Request["mobil"]))
                self.local_VQ_conn.lrem("searchMobil", 1, json.dumps(self.Request["mobil"]))
                logger.info("已经清理掉非会员用户:{}".format(self.Request["mobil"]))
                return False
        else:
            return False


    @retry(wait_fixed=1000)
    def search(self,company):
        try:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Referer": "https://www.tianyancha.com/advance/search",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1.txt",
                "Upgrade-Insecure-Requests": "1.txt",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "sec-ch-ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\""
            }
            self.session.cookies.set("auth_token", self.Request["token"])
            url = "https://www.tianyancha.com/search"
            params = {
                "key": company,
                # "sessionNo": self.Request["sessionNo"]
                "sessionNo": self.Request["searchSessionId"]
            }
            response = self.session.get(url, headers=headers, params=params,proxies=self.proxy_list())
            if response.status_code==200:
                if '<script id="__NEXT_DATA__" type="application/json">' in response.text:
                    html = etree.HTML(response.text)
                    json_date = json.loads(html.xpath('//script[@id="__NEXT_DATA__"]/text()')[0])
                    print(json_date)
                    if json_date["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]["state"] != "warn":
                        if json_date["page"] == "/search/[[...option]]":
                            # datas = json_date["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]["data"]["companyList"]
                            datas = \
                            json_date["props"]["pageProps"]["dehydratedState"]["queries"][2]["state"]["data"]["data"][
                                "companyList"]
                        else:
                            # datas =json_date["props"]["pageProps"]["dehydratedState"]["queries"][1.txt]["state"]["data"]["data"]["companyList"]
                            datas = json_date["props"]["pageProps"]["listRes"]["data"]["companyList"]
                        for data in datas:
                            company_name = str(data["name"]).replace("<em>", "").replace("</em>", "")
                            if data["id"]:
                                id = data["id"]
                                item={"company":company_name,"id":id}
                                print(item)
                                if self.conn.sismember(self.all_filter, company_name):
                                    self.conn.lpush(self.lp_redis,json.dumps(item))
                                    self.coll_2.insert_one(item)
                                    if "_id" in item:
                                        del item["_id"]
                                    self.coll.insert_one(item)
                                    logger.success(f"保存成功:{item}")
                                else:
                                    logger.error(f"未匹配到正确的公司名称:{company}")
                                    self.conn.sadd(self.error_company_name,company)
                            else:
                                logger.error("无id")
                    else:
                        self.Request["ua"] = get()
                        self.Request["proxy"] = self.proxy_list()
                        mobil = self.local_VQ_conn.lpop("searchMobil")
                        self.local_VQ_conn.rpush("searchMobil", mobil)
                        self.Request["mobil"] = json.loads(mobil)
                        self.get_cookie_csrf()
                        timestamp = int(time.time() - random.randint(50000, 60000))
                        self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758", "{},{},{},{}".
                                                 format(str(timestamp - random.randint(30000, 40000)),
                                                        str(timestamp - random.randint(20000, 30000)),
                                                        str(timestamp - random.randint(10000, 20000)),
                                                        str(timestamp)))
                        self.Request["searchSessionId"] = "{:.8f}".format(time.time())
                        self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758", str(int(time.time())))
                        raise Exception("掉线！！")
                else:
                    self.Request["ua"] = get()
                    self.Request["proxy"] = self.proxy_list()
                    mobil = self.local_VQ_conn.lpop("searchMobil")
                    self.local_VQ_conn.rpush("searchMobil", mobil)
                    self.Request["mobil"] = json.loads(mobil)
                    self.get_cookie_csrf()
                    timestamp = int(time.time() - random.randint(30000, 40000))
                    self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758", "{},{},{},{}".
                                             format(str(timestamp - random.randint(20000, 30000)),
                                                    str(timestamp - random.randint(10000, 20000)),
                                                    str(timestamp - random.randint(5000, 10000)),
                                                    str(timestamp)))
                    self.Request["searchSessionId"] = "{:.8f}".format(time.time())
                    self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758", str(int(time.time())))
                    raise Exception("掉线！！")
            elif response.status_code == 429:
                logger.error("429")
                refer = re.findall("访问网址：(.*?)</li>", response.text, re.S)[0]
                content = {"content": response.text, "refer":refer,"cookie": requests.utils.dict_from_cookiejar(self.session.cookies),
                           "UA": headers,"company": company}
                self.localconn.lpush("safe_verify", json.dumps(content))
                while True:
                    is_run = self.localconn.lpop("is_safe")
                    time.sleep(4)
                    if is_run is None:
                        print("超时")
                        raise Exception("状态刷新失败")
                    else:
                        if is_run.decode():
                            logger.success("状态刷新成功！！恢复采集....")
                            raise Exception("状态刷新")
                        else:
                            logger.error("状态刷新失败")
                            raise Exception("状态刷新失败")
            elif response.status_code == 406:
                self.Request["ua"] = get()
                self.Request["proxy"] = self.proxy_list()
                self.local_VQ_conn.sadd("ErrorMobil", json.dumps(self.Request["mobil"]))
                self.local_VQ_conn.lrem("searchMobil", 1, json.dumps(self.Request["mobil"]))
                mobil = self.local_VQ_conn.lpop("searchMobil")
                self.local_VQ_conn.rpush("searchMobil", mobil)
                self.Request["mobil"] = json.loads(mobil)
                self.get_cookie_csrf()
                timestamp = int(time.time() - random.randint(30000, 40000))
                self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758", "{},{},{},{}".
                                         format(str(timestamp - random.randint(20000, 30000)),
                                                str(timestamp - random.randint(10000, 20000)),
                                                str(timestamp - random.randint(5000, 10000)),
                                                str(timestamp)))
                self.Request["searchSessionId"] = "{:.8f}".format(time.time())
                self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758", str(int(time.time())))
                raise Exception("账号异常！！")
            else:
                logger.error(response.text)
                self.conn.sadd(self.flag,company)
        except KeyError as e:
            logger.error(company)
            logger.error(e)
        except Exception as e:
            logger.error(e)
            self.coll.insert_one(company)
            logger.warning(f"未正确解析公司：{company}")


    def main(self):
        with ThreadPoolExecutor(4) as f:
            self.Request["ua"] = get()
            self.Request["proxy"] = self.proxy_list()
            mobil = self.local_VQ_conn.lpop("searchMobil")
            self.local_VQ_conn.rpush("searchMobil", mobil)
            self.Request["mobil"] = json.loads(mobil)
            self.get_cookie_csrf()
            if self.is_VIP():
                timestamp = int(time.time() - random.randint(30000, 40000))
                self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758","{},{},{},{}".
                                         format(str(timestamp - random.randint(20000, 30000)),
                                                str(timestamp - random.randint(10000, 20000)),
                                                str(timestamp - random.randint(5000, 10000)),
                                                str(timestamp)))
                self.Request["searchSessionId"] = "{:.8f}".format(time.time())
                self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758",str(int(time.time())))
                _ = 1
                all_data = []
                # while True:
                res= self.conn.lrange("补id:补companyID",0,-1)
                    # res= self.conn.lrange("error_data:company_id",0,-1.txt)
                for company in res:
                    if _ % 1900==0:
                        self.Request["ua"]=get()
                        self.Request["proxy"]=self.proxy_list()
                        mobil = self.local_VQ_conn.lpop("searchMobil")
                        self.local_VQ_conn.rpush("searchMobil", mobil)
                        self.Request["mobil"] = json.loads(mobil)
                        self.get_cookie_csrf()
                        timestamp = int(time.time() - random.randint(30000, 40000))
                        self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758", "{},{},{},{}".
                                                 format(str(timestamp - random.randint(20000, 30000)),
                                                        str(timestamp - random.randint(10000, 20000)),
                                                        str(timestamp - random.randint(5000, 10000)),
                                                        str(timestamp)))
                        self.Request["sessionNo"] = "{:.8f}".format(time.time())
                        self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758", str(int(time.time())))
                    # company=self.conn.lpop("补id:补companyID")
                    company=json.loads(company)["company_name"]
                    # company=company.decode("utf-8")
                    print(company)
                    if self.conn.sadd(self.all_filter, company):
                        all_data.append(f.submit(self.search,company=company))
                        # self.search(company)
                    else:
                        logger.warning(f"【*】公司名字已过滤:{company}")
                    if len(all_data) >= 50:
                        for future in all_data:
                            try:
                                future.result()
                            except Exception as e:
                                logger.error(e)
                                future.result()
                    _ += 1
                    logger.info(f"。。。。。。。。。。。第{_}页")
                for future in all_data:
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(e)
                        future.result()
            else:
                logger.error("{}:非会员用户!!".format(self.Request["mobil"]))
                self.main()



if __name__ == '__main__':
    sc = SuccessCODE()
    sc.main()




