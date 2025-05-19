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
import os
import random
import uuid
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
# from curl_cffi import requests as cffi_requests


ocr = ddddocr.DdddOcr(det=False, ocr=False)
ocr2 = ddddocr.DdddOcr(det=True)


class CC1(object):

    def __init__(self):
        # self.username = "18Klove"
        # password = "666666".encode('utf8')
        self.username = "17850010007"
        password = "anbo1234".encode('utf8')
        self.password = hashlib.md5(password).hexdigest()
        self.soft_id ='9501'
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
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


class CC2:
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

class CC:
    def PostPic(self,pic_list):
        if len(pic_list) == 4:
            pic_list.append("")
        tmp = str(time.time())
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        }
        url = "http://192.168.5.181:10121/geetest4_word/gradio_api/queue/"
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

class SuccessCODE():

    def __init__(self):
        self.session = requests.Session()
        self.local_conn = redis.Redis(host='192.168.5.167', port=10284, db=0, password="e8Mzr}$%jsuCxKn4r#mm", socket_connect_timeout=170)
        self.local_VQ_conn = redis.Redis(host='192.168.5.181', port=10281, db=0, password="*s,8<[VVS6h.nnWZ=cv{",socket_connect_timeout=70)
        self.Reqest={}

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
        dir_path = f"F:/yl/datasets/imgs/{type}/{uuid}"
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
                "challenge": "09d9c310-e098-467a-8b6c-c61ae6642e3c",
                "client_type": "web",
                "lang": "zho"
            }
            response = self.session.get(url, headers=headers, params=params, proxies=self.Reqest["proxy"])
            if response.status_code == 200:
                cookies = response.cookies.get("captcha_v4_user")
                resp = json.loads(response.text.strip("(").strip(")"))
                # print(res)
                type = resp["data"]['captcha_type']
                lot_number = resp["data"]["lot_number"]
                process_token = resp["data"]["process_token"]
                pow_detail = resp["data"]["pow_detail"]
                pow_detail = [pow_detail[i] for i in pow_detail if isinstance(pow_detail, dict)]
                payload = resp["data"]["payload"]
                static_path =resp["data"]["static_path"]
                params_list = {
                    "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
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
                    q_list =resp["data"]['ques']
                    bytes_list = []
                    for index, img_url in enumerate(q_list):
                        tag = requests.get("https://static.geetest.com/" + img_url).content
                        # word_pic = ImageProcess.wordprocess(tag)
                        # self.download_img(tag, str(index), type, uuid1)
                        word_pic=base64.b64encode(tag).decode("utf-8")
                        bytes_list.append(word_pic)
                    imgs_url = "https://static.geetest.com/" + resp["data"]['imgs']
                    slide_bytes = requests.get(imgs_url).content
                    # new_pic = ImageProcess.mergePic(slide_bytes, bytes_list)
                    new_pic =[base64.b64encode(slide_bytes).decode("utf-8")]+bytes_list
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
                    # self.download_img(bg_bytes, "bg_img", type, uuid1)
                    # self.download_img(target_bytes, "slide_img", type, uuid1)
                    params_list["dis"] = dis
                    params_list["type"] = "slide"
                return params_list
        except Exception as e:
            logger.error(e)


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

    @retry(wait_fixed=1000, stop_max_attempt_number=5)
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
        par["par_param"] =  {'rw0k': 'cpej'}
        param = self.Composite_parameter(par["lot_number"])
        jscode = open("../RiskcontrolPass/jscode/w_decode.js", encoding="utf-8", errors="ignore").read()
        data = execjs.compile(jscode).call("_fff", par, par["par_param"], param)
        params = {
            "captcha_id": par["captcha_id"],
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
            lot_number = resp["data"]["seccode"]["lot_number"]
            pass_token = resp["data"]["seccode"]["pass_token"]
            self.Reqest["sign"] = data["pow_sign"]
            params_list1 = {
                "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
                "lot_number": lot_number,
                "pass_token": pass_token,
                "gen_time": gen_time,
                "captcha_output": captcha_output
            }
            return params_list1
        else:
            logger.error(f"请求状态码:{response.status_code}")

    def get_3(self):
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
                                        proxies=self.Reqest["proxy"])
        except:
            time.sleep(0.5)
            response = self.session.get(url,headers=headers,params=params,proxies=self.Reqest["proxy"])
        res = json.loads(str(response.text).strip("(").strip(")"))
        print(res)
        if res["message"] == "":
            token = res["data"]['token']
            id = str(res["data"]['userId'])
            self.create_cookie(id, self.Reqest["mobil"]["mobil"])
            logger.success("登录成功，同学开始愉快的玩耍吧！！")
            logger.info("【R】{}用户登录已成功！获取的sign：{}".format(id, token))
            self.Reqest["userid"] = id
            self.Reqest["token"] = token
            self.get_cookie_csrf()
            return True
        elif res["message"]=="账号存在风险，暂不能操作" or "输入的手机号码与密码不匹配，推荐使用短信登录" or "密码登录冻结，请使用验证码登录" or response.status_code==406:
            key = self.Reqest["mobil"]["keys"]
            if "keys" in self.Reqest["mobil"]:
                del self.Reqest["mobil"]["keys"]
            self.local_VQ_conn.sadd("ErrorMobil", json.dumps(self.Reqest["mobil"]))
            self.local_VQ_conn.lrem(key, 1, json.dumps(self.Reqest["mobil"]))
            return False
        else:
            logger.error(f"登陆异常: {res}")
            return False

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
            "User-Agent": self.Reqest["ua"],
            "X-AUTH-TOKEN": self.Reqest["token"],
            "X-TYCID":self.Reqest["X-TYCID"],
            "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://napi-huawei.tianyancha.com/next/web/getUserInfo"
        params = {
            "_": str(int(time.time() * 1000))
        }
        response = self.session.get(url, headers=headers, params=params,proxies=self.Reqest["proxy"])
        print(response.text)
        if response.status_code == 200:
            if "isVip" in response.json()["data"]:
                logger.success("【*】会员用户:{}!!".format(self.Reqest["mobil"]))
                return True
            else:
                self.local_VQ_conn.sadd("LoginUser", json.dumps(self.Reqest["mobil"]))
                keys=self.Reqest["mobil"]["keys"]
                if "keys" in self.Reqest["mobil"]:
                    del self.Reqest["mobil"]["keys"]
                self.local_VQ_conn.lrem(keys, 1, json.dumps(self.Reqest["mobil"]))
                logger.info("已经清理掉非会员用户:{}".format(self.Reqest["mobil"]))
                return False
        else:
            return False

    @retry(wait_fixed=1000, stop_max_attempt_number=5)
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
        self.session.get("https://www.tianyancha.com/", headers=headers, proxies=self.Reqest["proxy"],timeout=10)
        self.Reqest["X-TYCID"]=self.session.cookies.get("TYCID")
        self.Reqest["CUID"] = self.session.cookies.get("CUID")
        headers = {
            'Referer': 'https://www.tianyancha.com/',
        }
        self.session.get('https://hm.baidu.com/hm.js?e92c8d65d92d534b0fc290df538b4758',
                         headers=headers,proxies=self.Reqest["proxy"],timeout=10)

    def create_cookie(self, id, m):
        js_code = open("../RiskcontrolPass/jscode/signCook.js", encoding="utf-8").read()
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
        # self.session.cookies.set("tyc-user-phone", "%255B%252218587162714%2522%255D")
        self.session.cookies.set("tyc-user-phone", "%255B%252218805000600%2522%252C%2522186%25208985%25208765%2522%252C%2522155%25208941%25205730%2522%252C%2522130%25200867%25206042%2522%255D")

    @retry(wait_fixed=1000)
    def proxy_list(self):
            global l
            l = random.randint(1, 6)
            # 隧道域名:端口号
            tunnel = "g385.kdltps.com:15818"
            # 用户名密码方式
            username = "t13509625111642"
            password = "bc66r4oi:%d" % l
            proxies = {
                "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
                "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
            }
            # try:
            #     resp = requests.get("https://myip.ipip.net", proxies=proxies,timeout=20)
            #     if resp.status_code == 200:
            #         print(resp.text)
            #         return proxies
            #     else:
            #         raise  "proxy error"
            # except Exception as e:
            #     logger.error(e)
            return None

    def safecookie(self):
        timestamp = int(time.time() - random.randint(30000, 40000))
        self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758", "{},{},{},{}".
                                 format(str(timestamp - random.randint(20000, 30000)),
                                        str(timestamp - random.randint(10000, 20000)),
                                        str(timestamp - random.randint(5000, 10000)),
                                        str(timestamp)))
        self.Reqest["sessionNo"] = "{:.8f}".format(time.time())
        self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758", str(int(time.time())))
        cookie_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        print("======cookie_dict:", {
            "cookie_dict": cookie_dict,
            "ua": self.Reqest["ua"],
            "pchannel":l,
            "token": self.Reqest["token"],
            "TYCID":self.Reqest["X-TYCID"],
            "sign": self.Reqest["sign"],
            "userid": self.Reqest["userid"],
            "sessionNo": self.Reqest["sessionNo"],
            "mobil": self.Reqest["mobil"],
        })
        cookie_data = {
            "cookie_dict": cookie_dict,
            "ua": self.Reqest["ua"],
            "pchannel": l,
            "token": self.Reqest["token"],
            "TYCID": self.Reqest["X-TYCID"],
            "sign": self.Reqest["sign"],
            "userid": self.Reqest["userid"],
            "sessionNo": self.Reqest["sessionNo"],
            "mobil": self.Reqest["mobil"]
        }
        return cookie_data

    def main(self,mobil,flg,num):
            self.Reqest["ua"] = get()
            self.Reqest["proxy"] = self.proxy_list()
            self.Reqest["mobil"] = mobil
            self.get_3()
            if self.Reqest["mobil"]["keys"]!="LoginUser":
            # if self.Reqest["mobil"]["keys"]!="test1":
                if self.is_VIP():
                    cookie_data=self.safecookie()
                    for _ in range(num):
                        if flg == 1:
                            # self.local_VQ_conn.lpush("searchCookie",json.dumps(cookie_data))
                            self.local_VQ_conn.lpush("testCookie",json.dumps(cookie_data))
                        elif flg==3:
                            self.local_VQ_conn.lpush("sifaCookie", json.dumps(cookie_data))
                        else:
                            self.local_VQ_conn.lpush("detailCookie", json.dumps(cookie_data))
                    logger.success("已完成任务！！")
                else:
                    logger.error("{}:非会员用户!!".format(self.Reqest["mobil"]))
                return True
            else:
                cookie_data=self.safecookie()
                for _ in range(num):
                        self.local_VQ_conn.lpush("NoMemeryCookie", json.dumps(cookie_data))
                        # self.local_VQ_conn.lpush("testCookie", json.dumps(cookie_data))
                logger.success("已完成任务！！")
                return True

