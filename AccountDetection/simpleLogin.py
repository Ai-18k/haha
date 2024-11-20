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
import re
import time
import uuid
from urllib.parse import quote
import cv2
import execjs
import redis
import requests
from loguru import logger
from retrying import retry
import ddddocr

from AccountDetection import ImageProcess


@retry(wait_fixed=1)
def proxy_list():
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
    # resp = requests.get("https://myip.ipip.net", proxies=proxies)
    # if resp.status_code==200:
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


@retry(wait_fixed=1)
class CC:
    def PostPic(self,pic_list):
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
                        if "output" not in data:
                            logger.error("识别失败")
                            raise Exception("识别失败！！")
                        plan = json.loads(data)["output"]["data"][1]
                        for crop in plan:
                            x1, y1, x2, y2 = crop
                            xy.append([(x1 + x2) / 2, (y1 + y2) / 2])
                        return xy

local_VQ_conn = redis.Redis(host='192.168.5.181', port=7933, db=0, password="fer@nhaweif576KUG",socket_connect_timeout=70)

class Login_module:

    def __init__(self,mobil):
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
        dir_path = f"E:/AIProject/Datesets/imgs/imgs/{type}/{uuid}"
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
        _uuid=uuid.uuid1()
        params = {
            # "callback": "geetest_1726673346207",
            "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
            "challenge":_uuid,
            "client_type": "web",
            "lang": "zho"
        }
        response = self.session.get(url, headers=headers, params=params, proxies=self.Reqest["proxy"])
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
            uuid1 = uuid.uuid1()
            if type == 'word':
                print(">>>>>>>>>>>>>>>>>>>>>>>>点选>>>>>>>>>>>>>>")
                q_list = res["data"]['ques']
                bytes_list = []
                for index, img_url in enumerate(q_list):
                    tag = requests.get("https://static.geetest.com/" + img_url).content
                    # self.download_img(tag, str(index), type, uuid1)
                    # word_pic = ImageProcess.wordprocess(tag)
                    word_pic=base64.b64encode(tag).decode("utf-8")
                    bytes_list.append(word_pic)
                imgs_url = "https://static.geetest.com/" + res["data"]['imgs']
                slide_bytes = requests.get(imgs_url).content
                # new_pic = ImageProcess.mergePic(slide_bytes, bytes_list)
                new_pic=[base64.b64encode(slide_bytes).decode("utf-8")]+bytes_list
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
                slide_url = "https://static.geetest.com/" + res["data"]['slice']
                bg_url = "https://static.geetest.com/" + res["data"]['bg']
                # print("slide_img:" + slide_url)
                # print("bg_img:" + bg_url)
                target_bytes = requests.get(slide_url).content
                bg_bytes = requests.get(bg_url).content
                dis = ocr.slide_match(target_bytes, bg_bytes, simple_target=True)["target"][0]
                # logger.info(dis)
                self.download_img(bg_bytes, "bg_img", type, uuid1)
                self.download_img(target_bytes, "slide_img", type, uuid1)
                params_list["dis"] = dis
                params_list["type"] = "slide"
            return params_list


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
        url = "https://static.geetest.com" + params_list[
            "static_path"] + "/js/gcaptcha4.js"
        response = self.session.get(url,headers=headers, proxies=self.Reqest["proxy"])
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
                    "User-Agent":self.Reqest["ua"],
                    "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", "
                                 "\"Chromium\";v=\"123\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\""
                    }
            url = "https://gcaptcha4.geetest.com/verify"
            res = self.re_js_code()
            jscode = open("w_decode.js", encoding="utf-8").read()
            data = execjs.compile(jscode).call("_fff", res["par_data"], res["par_param"])
            params = {
                "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
                "client_type": "web",
                "lot_number": res["par_data"]["lot_number"],
                "payload": res["par_data"]["payload"],
                "process_token": res["par_data"]["process_token"],
                "payload_protocol": "1",
                "pt": "1",
                "w": data["res"]
            }
            response = self.session.get(url,headers=headers,params=params,proxies=self.Reqest["proxy"])
            if response.status_code == 200:
                res = json.loads(str(response.text).strip("(").strip(")"))
                gen_time = res.get("data").get("seccode")["gen_time"]
                captcha_output = res.get("data").get("seccode")["captcha_output"]
                captcha_id = res.get("data").get("seccode")["captcha_id"]
                lot_number = res.get("data").get("seccode")["lot_number"]
                pass_token = res.get("data").get("seccode")["pass_token"]
                self.Reqest["sign"]=data["pow_sign"]
                params_list1 = {
                        "lot_number": lot_number,
                        "pass_token": pass_token,
                        "gen_time": gen_time,
                        "captcha_output": captcha_output
                }
                return params_list1
            else:
                logger.error(f"请求状态码:{response.status_code}")
        except Exception as e:
            logger.error("验证滑块异常:{}".format(e))


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
                "User-Agent":self.Reqest["ua"],
                "X-TYCID": self.Reqest["X-TYCID"],
                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", "
                             "\"Chromium\";v=\"114\", \"Google "
                             "Chrome\";v=\"114\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\""
                }
        url = "https://napi-huawei.tianyancha.com/next/web/cdloginv2_validatev2"
        params = {
                "mobile": self.mobil["mobil"],
                "cdpassword": hashlib.md5(self.mobil["pwd"].encode("utf-8")).hexdigest(),  # md5算法
                "loginway": "PL",
                "captcha_id":  "517df78b31ff1b8f841cd86fc0db9f3e",
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
                    return True
                elif res["message"]=="账号存在风险，暂不能操作":
                    logger.error("{}:{}".format(self.mobil,response.json()["message"]))
                    local_VQ_conn.sadd("ErrorUser",json.dumps(self.mobil))
                    with open("C:/Users/Administrator/Desktop/账号被封.txt", "a", encoding="utf-8") as f:
                        f.write(self.mobil["mobil"] + "密码" + self.mobil["pwd"] + "\n")
                    return False
                elif "密码登录冻结，请使用验证码登录" in res["message"]:
                    print(res["message"])
                    logger.error("{}:{}".format(self.mobil, "密码登录冻结，请使用验证码登录"))
                    local_VQ_conn.sadd("ErrorPwd", json.dumps(self.mobil))
                else:
                    logger.error(res)
                    return False
            else:
                logger.error(f"{self.mobil}:账号密码错误!!")
                with open("C:/Users/Administrator/Desktop/账号密码错误.txt","a",encoding="utf-8")as f:
                        f.write(self.mobil["mobil"]+"密码"+self.mobil["pwd"]+"\n")
                local_VQ_conn.sadd("ErrorPwd", json.dumps(self.mobil))
                return False
        else:
            logger.error(f"{self.mobil}：账号异常无法登陆!!")
            with open("C:/Users/Administrator/Desktop/账号异常无法登陆.txt","a",encoding="utf-8")as f:
                        f.write(self.mobil["mobil"]+"密码"+self.mobil["pwd"]+"\n")
            return False


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
        headers = {
            'Referer': 'https://www.tianyancha.com/',
        }
        self.session.get('https://hm.baidu.com/hm.js?e92c8d65d92d534b0fc290df538b4758', headers=headers)
        

    def main(self,proxy,ua):
        self.Reqest["proxy"]=proxy
        self.Reqest["ua"]=ua
        if self.get_3():
            return self.session,self.Reqest
        else:
            return False
    
