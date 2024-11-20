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
import base64
import io
import math
import uuid
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
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
from retrying import retry
import ddddocr
from io import BytesIO
import cv2
from PIL import Image

from FunComponent.AccountDetection import ImageProcess

ocr = ddddocr.DdddOcr(det=False, ocr=False,show_ad=False)
ocr1 = ddddocr.DdddOcr(beta=True,show_ad=False)  # 切换为第二套ocr模型
ocr2 = ddddocr.DdddOcr(det=True,show_ad=False)


class CC11:
    def PostPic(self,img:bytes,codesore:str):
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
            data=response.json()
            _crop=data["data"]["res"]["crop_centre"]
            return _crop
        else:
            return None

class CC:
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
            data=response.json()
            _crop=data["data"]["res"]["crop_centre"]
            return _crop
        else:
           raise Exception("链接失效")


class SuccessCODE():

    def __init__(self):
        self.client = MongoClient(host='127.0.0.1', port=27017)
        self.local_conn = redis.Redis(host='127.0.0.1', port=7980, db=0, password="qwe!@#SDF345788",
                                      socket_connect_timeout=1170)
        self.session = requests.session()
        self.coll = self.client["test"]["company_id"]  
        self.Request={}
        self.filter = "test:filter:company_id"
        self.filter_params = "test:filter:params"
        self.com_id = "test:company_id"
        self.params="test:params"


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
        # try:
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
            "challenge": "09d9c310-e098-467a-8b6c-c61ae6642e3c",
            "client_type": "web",
            "lang": "zho"
        }
        response = self.session.get(url, headers=headers, params=params, proxies=self.Request["proxy"])
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
                "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
                "lot_number": lot_number,
                "process_token": process_token,
                "pow_detail": pow_detail,
                "payload": payload,
                "cookies": cookies,
                "static_path": static_path
            }
            # uuid1 = uuid.uuid1()
            if type == 'word':
                print(">>>>>>>>>>>>>>>>>>>>>>>>点选>>>>>>>>>>>>>>")
                q_list = res["data"]['ques']
                # word_list = []
                # for index, img_url in enumerate(q_list):
                #     tag = requests.get("https://static.geetest.com/" + img_url).content
                #     # self.download_img(tag, str(index), type, uuid1)
                #     tag = Image.open(BytesIO(tag))
                #     white_bg = Image.new("RGBA", tag.size, (255, 255, 255, 255))
                #     white_bg.paste(tag, (0, 0), tag)
                #     result = ocr1.classification(white_bg, png_fix=True)
                #     word_list.append(result)
                # imgs_url = "https://static.geetest.com/" + res["data"]['imgs']
                # slide_bytes = requests.get(imgs_url).content
                # word_str = "".join(i for i in word_list)
                # click_list = CC().PostPic(slide_bytes, word_str)
                bytes_list = []
                for index, img_url in enumerate(q_list):
                    tag = requests.get("https://static.geetest.com/" + img_url).content
                    # self.download_img(tag, str(index), type, uuid1)
                    word_pic = ImageProcess.wordprocess(tag)
                    bytes_list.append(word_pic)
                imgs_url = "https://static.geetest.com/" + res["data"]['imgs']
                slide_bytes = requests.get(imgs_url).content
                new_pic = ImageProcess.mergePic(slide_bytes, bytes_list)
                click_list = CC().PostPic(new_pic)
                click_smark = []
                for _word in click_list:
                    click_smark.append([round(int(_word[0]) * 100 / 3), round(int(_word[1]) * 50)])
                # self.download_img(slide_bytes, "click_img", type, uuid1)
                logger.info(click_smark)
                params_list["smark"] = click_smark
                params_list["type"] = "word"
            elif type == 'slide':
                print(">>>>>>>>>>>>>>>>>>>>>>>>滑块>>>>>>>>>>>>>>")
                slide_url = "https://static.geetest.com/" + res["data"]['slice']
                bg_url = "https://static.geetest.com/" + res["data"]['bg']
                # print("slide_img:" + slide_url)
                # print("bg_img:" + bg_url)
                target_bytes = requests.get(slide_url).content
                bg_bytes = requests.get(bg_url).content
                dis = ocr.slide_match(target_bytes, bg_bytes, simple_target=True)["target"][0]
                logger.info(dis)
                # self.download_img(bg_bytes, "bg_img", type, uuid1)
                # self.download_img(target_bytes, "slide_img", type, uuid1)
                params_list["dis"] = dis
                params_list["type"] = "slide"
            return params_list


    def re_js_code(self):

            params_list=self.get_1()
            headers = {
                    "Host": "static.geetest.com",
                    "pragma": "no-cache",
                    "cache-control": "no-cache",
                    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                                 "Chrome\";v=\"114\"",
                    "origin": "https://www.tianyancha.com",
                    "dnt": "1",
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
            # logger.info("【R】>>>>>>正在解析js......")
            response = self.session.get(url,headers=headers,proxies=self.Request["proxy"])
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
            matche_05 = re.search(r'\{".*?}};', text, re.S)
            str_code += "return " + matche_05.group() + "};"
            res = execjs.compile(str_code).call("get_param")
            return {"par_param":res,"par_data":params_list}



    def get_2(self):
        try:
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
            res=self.re_js_code()
            logger.info(f"》》》》》》正在获取js参数............")
            jscode = open("../../RiskcontrolPass/jscode/w_decode.js", encoding="utf-8").read()
            data = execjs.compile(jscode).call("_fff", res["par_data"], res["par_param"])
            logger.info(data)
            params = {
                "captcha_id": res["par_data"]["captcha_id"],
                "client_type": "web",
                "lot_number": res["par_data"]["lot_number"],
                "payload": res["par_data"]["payload"],
                "process_token": res["par_data"]["process_token"],
                "payload_protocol": "1",
                "pt": "1",
                "w": data["res"]
            }
            response = self.session.get(url,
                    headers=headers,
                    params=params,
                    proxies=self.Request["proxy"])
            if response.status_code == 200:
                resp = json.loads(str(response.text).strip("(").strip(")"))
                print(resp)
                gen_time =resp["data"]["seccode"]["gen_time"]
                captcha_output =resp["data"]["seccode"]["captcha_output"]
                captcha_id = resp["data"]["seccode"]["captcha_id"]
                lot_number = resp["data"]["seccode"]["lot_number"]
                pass_token = resp["data"]["seccode"]["pass_token"]
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
                    id=str(res["data"]['userId'])
                    self.Request["userid"]=id
                    self.create_cookie(self.Request["mobil"]["mobil"],id)
                    logger.success("登录成功，同学开始愉快的玩耍吧！！")
                    logger.info("【R】{}用户登录已成功！获取的sign：{}".format(id, token))
                    return token, data["pow_sign"]
                elif res["message"]=="账号存在风险，暂不能操作" or "输入的手机号码与密码不匹配，推荐使用短信登录":
                    self.local_conn.sadd("ErrorMobil", json.dumps(self.Request["mobil"]))
                    self.local_conn.lrem("testMobil", 1, json.dumps(self.Request["mobil"]))
                    mobil = self.local_conn.lpop("testMobil")
                    self.local_conn.rpush("testMobil", mobil)
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
        token, sign = self.get_3()
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
        self.session.cookies.set("auth_token", token)
        url = "https://www.tianyancha.com/"
        try:
            self.session.get(url, headers=headers, proxies=self.Request["proxy"])
        except:
            time.sleep(2)
            self.session.get(url, headers=headers, proxies=self.Request["proxy"])
        self.Request["token"] = token
        self.Request["sign"] = sign

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
        return proxies
        # return None
        # else:
        #     raise Exception("请求代理")


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
                    "X-TYCID": self.Request["sign"],
                    "X-AUTH-TOKEN": self.Request["token"]
                })
                url = "https://capi.tianyancha.com/cloud-tempest/web/searchCompanyV4"
                params = {
                    "_": str(int(time.time() * 1000))
                }
                data = {
                    "filterJson": "{\"economicTypeMethod\":{\"key\":\"economicTypeMethod\",\"items\":[{\"value\":\"1\"}]},\"institutionTypeMethod\":{\"key\":\"institutionTypeMethod\",\"items\":[{\"value\":\"0\"}]},\"word\":{\"key\":\"word\",\"items\":[{\"value\":\"\"}]},\"areaCode\":{\"key\":\"areaCode\",\"items\":[{\"value\":%s}]},\"establishTimeRange\":{\"key\":\"establishTimeRange\",\"items\":[{\"value\":%s},{\"value\":%s}]},\"institutionType\":{\"key\":\"institutionType\",\"items\":[{\"value\":\"个体工商户\"},{\"value\":\"全民所有制\"},{\"value\":\"集体所有制\"},{\"value\":\"联营企业\"},{\"value\":\"农民专业合作社\"},{\"value\":\"事业单位\"},{\"value\":\"学校\"}]}}"%(info["areaCode"],info["new_day"],info["next_day"]),
                    "searchType": 1,
                    "sessionNo": self.Request["sessionNo"],
                    "allowModifyQuery": 1,
                    "reportInfo": {
                        "page_id": "SearchResult",
                        "page_name": "主搜搜索结果页",
                        "tab_id": "company",
                        "tab_name": "公司",
                        "search_session_id": self.Request["sessionNo"],
                        "distinct_id": self.Request["userid"]
                    },
                    "pageNum": page,
                    "pageSize": 20
                }
                str_data = json.dumps(data, separators=(',', ':'))
                response = self.session.post(url,params=params,data=str_data,proxies=self.proxy_list())
                logger.info(info)
                logger.info(self.Request["mobil"])
                logger.info(response.status_code)
                if response.status_code == 200:
                    if response.json()["errorCode"] == "":
                        if "data" in response.json() and "companyList" in response.json()["data"]:
                            num=math.ceil(response.json()["data"]["companyTotal"] / 20) if response.json()["data"]["companyTotal"] else 0
                            logger.info(f'这个链接共{num}页数据')
                            logger.info(f'当前是第{page}页')
                            if page > num:
                                break
                            compList = response.json().get("data").get("companyList")
                            for item in compList:
                                res = self.local_conn.sadd(self.filter, item["name"])
                                if res:
                                    info.update({"company": item["name"], "id": item["id"]})
                                    self.coll.insert_one(info)
                                    if "_id" in info:
                                        del info["_id"]
                                    self.local_conn.lpush(self.com_id, json.dumps(info))
                                    logger.success(info)
                                else:
                                    logger.warning("【*】已过滤:{}".format({"company": item["name"], "id": item["id"]}))
                        else:
                            # logger.info(response.text)
                            print("1>>>>>>>>>>>>>>>>>%s" % response.text)
                            time.sleep(1)
                            mobil = self.local_conn.lpop("testMobil")
                            self.local_conn.rpush("testMobil", mobil)
                            self.Request["mobil"] = json.loads(mobil)
                            self.Request["ua"] = get()
                            self.Request["proxy"] = self.proxy_list()
                            self.get_cookie_csrf()
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
                    elif response.json()["errorCode"] ==302004:
                        print("2 >>>>>>>>>>>>>", response.text)
                        time.sleep(1)
                        mobil = self.local_conn.lpop("testMobil")
                        self.local_conn.rpush("testMobil", mobil)
                        self.Request["mobil"] = json.loads(mobil)
                        self.Request["ua"] = get()
                        self.Request["proxy"] = self.proxy_list()
                        self.get_cookie_csrf()
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
                    elif response.json()["errorCode"] ==303000:
                        print("3 >>>>>>>>>>>>>", response.text)
                        self.local_conn.sadd("ErrorMobil", json.dumps(self.Request["mobil"]))
                        self.local_conn.lrem("testMobil", 1, json.dumps(self.Request["mobil"]))
                        mobil = self.local_conn.lpop("testMobil")
                        self.local_conn.rpush("testMobil", mobil)
                        self.Request["mobil"] = json.loads(mobil)
                        self.Request["ua"] = get()
                        self.Request["proxy"] = self.proxy_list()
                        self.get_cookie_csrf()
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
                    else:
                        print("4>>>>>>>>>>>>>>>>>%s"%response.text)
                        # raise Exception(f"HTTP status code {response.status_code} received.")
                        time.sleep(20)
                        self.next_page(info,page)
                        break
                else:
                    print("有风控?")
                page+=1
            except Exception as e:
                logger.error(e)
                self.local_conn.lpush("test:fail_params",json.dumps(info))


    def main(self):
        with ThreadPoolExecutor(2) as f:
            self.Request["ua"] = get()
            self.Request["proxy"] = self.proxy_list()
            mobil = self.local_conn.lpop("testMobil")
            self.local_conn.rpush("testMobil", mobil)
            self.Request["mobil"] = json.loads(mobil)
            self.get_cookie_csrf()
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
                    if _ % 200==0:
                        self.Request["ua"]=get()
                        self.Request["proxy"]=self.proxy_list()
                        mobil = self.local_conn.lpop("testMobil")
                        self.local_conn.rpush("testMobil", mobil)
                        self.Request["mobil"] = json.loads(mobil)
                        self.get_cookie_csrf()
                        timestamp = int(time.time() - random.randint(50000,60000))
                        self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758", "{},{},{},{}".
                                                 format(str(timestamp - random.randint(30000, 40000)),
                                                        str(timestamp - random.randint(20000, 30000)),
                                                        str(timestamp - random.randint(10000, 20000)),
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
                            # futures.append(f.submit(self.next_page,info=info,page=1))
                            self.next_page(info,1)
                        else:
                            logger.warning(f"【*】参数已经存在:{info}")
                    else:
                        logger.warning("{}:存在company_id".format(info))
                    # if len(futures)>=100:
                    #     for future in futures:
                    #         try:
                    #             future.result()
                    #         except Exception as e:
                    #             logger.error(e)
                    #             time.sleep(1)
                    #             future.result()
                    #     futures.clear()
                    _ += 1
                    logger.info(f"。。。。。。。。。。。。这是第 {_} 家公司")
                except redis.exceptions.TimeoutError as e:
                    logger.error(e)
                    self.main()
                    return
            # for future in futures:
            #     try:
            #         future.result()
            #     except:
            #         logger.error(e)
            #         time.sleep(1)
            #         future.result()


if __name__ == '__main__':
    sc = SuccessCODE()
    sc.main()
