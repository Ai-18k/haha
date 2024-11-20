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
from feapder.network.user_agent import get
import requests
import json
from loguru import logger
import execjs
import hashlib
import time
from urllib.parse import quote
import re
from redis import Redis
from retrying import retry


class SuccessCODE():

    def __init__(self):
        self.session = requests.session()
        # self.conn = Redis(host='139.9.70.234', port=6379, db=2, password="anbo123",socket_connect_timeout=70)
        self.conn = Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=70)
        self.local_VQ_conn = Redis(host='192.168.5.181', port=7933, db=0, password="fer@nhaweif576KUG",
                              socket_connect_timeout=70)

        self.Request={}

    def get_1(self):
        headers = {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1.txt",
            "Pragma": "no-cache",
            "Referer": "https://www.geetest.com/",
            "Sec-Fetch-Dest": "script",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": self.Request["ua"],
            "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", "
                         "\"Chromium\";v=\"123\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://gcaptcha4.geetest.com/load"
        params = {
            # "callback": "geetest_1712670589441",
            "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
            "challenge": "09d9c310-e098-467a-8b6c-c61ae6642e3c",
            "client_type": "web",
            "lang": "zho"
        }
        response = self.session.get(url,
                                    headers=headers,
                                    params=params,
                                    proxies=self.Request["proxy"])
        if response.status_code == 200:
            cookies = response.cookies.get("captcha_v4_user")
            res = json.loads(str(response.text).strip("(").strip(")"))
            lot_number = res.get("data").get("lot_number")
            process_token = res.get("data").get("process_token")
            pow_detail = res.get("data").get("pow_detail")
            static_path = res.get("data").get("static_path")
            if isinstance(pow_detail, dict):
                pow_detail = [pow_detail[i] for i in pow_detail]
            payload = res.get("data").get("payload")
            params_list = {
                "captcha_id": params["captcha_id"],
                "lot_number": lot_number,
                "process_token": process_token,
                "pow_detail": pow_detail,
                "payload": payload,
                "cookies": cookies,
                "static_path": static_path
            }
            return params_list

    def re_js_code(self):
        # proxy = cls.proxy_list()
        # UserAgent = get("chrome")
        params_list = self.get_1()
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
        url = "https://static.geetest.com" + params_list["static_path"] + "/js/gcaptcha4.js"
        logger.info("【R】>>>>>>正在解析js......")
        response = self.session.get(url, headers=headers, proxies=self.Request["proxy"])
        str_code = ""
        match = re.search(r'(.*?)\.', response.text)
        head = match.group().strip(".")
        # 用正则表达式匹配  找到gyMNB.****}();  前两个函数内容
        matche_01 = re.findall(rf"{head}\..*?\}}\(\);", response.text)
        str_code += matche_01[0] + matche_01[1]
        matche_02 = re.findall(rf'{head}\..*?}};', response.text)
        str_code += matche_02[2] + matche_02[3] + f"function {head}() {{}};"
        # 找到自执行函数
        matche_03 = re.search(r"!function\(\){var.*?};}\(\)", response.text)
        text = matche_03.group()
        # 找到还原方法
        matche_04 = re.search(r"var.*?];", text)
        str_code += "function get_param(){" + matche_04.group()
        # 找到参数列表
        matche_05 = re.search(r'\{".*?\)}', text)
        str_code += "return " + matche_05.group() + "};"
        res = execjs.compile(str_code).call("get_param")
        return res

    def get_2(self, flag):
        try:
            p = self.get_1()
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
            par = self.re_js_code()
            logger.info(f"【R】获取js参数：{par}")
            if flag == 1:
                jscode=open("../RiskcontrolPass/jscode/w_decode.js", encoding="utf-8").read()
                data = execjs.compile(jscode).call("_fff", p, par)
            else:
                jscode1=open("../RiskcontrolPass/jscode/w_decode_1.js", encoding="utf-8").read()
                data = execjs.compile(jscode1).call("_fff_a", p)
            cookies = {
                "captcha_v4_user": p["cookies"]
            }
            params = {
                "captcha_id": p["captcha_id"],
                "client_type": "web",
                "lot_number": p["lot_number"],
                "payload": p["payload"],
                "process_token": p["process_token"],
                "payload_protocol": "1.txt",
                "pt": "1.txt",
                "w": data["res"]
            }
            response = self.session.get(url,
                                        headers=headers,
                                        cookies=cookies,
                                        params=params,
                                        proxies=self.Request["proxy"])
            if response.status_code == 200:
                res = json.loads(str(response.text).strip("(").strip(")"))
                if res["data"]["result"] == 'continue':
                    par = self.re_js_code()
                    js_code_1 = open("../RiskcontrolPass/jscode/R.config", encoding="utf-8").read()
                    js_code = '''
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
                       "biht": "1426265548",''' + f'"{list(par)[0]}":"{par[list(par)[0]]}",' + \
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
                    with open("../RiskcontrolPass/jscode/w_decode_1.js", "w", encoding="utf-8") as f:
                        f.write(js_code_1 + js_code)
                    self.Request["proxy"]=self.proxy_list()
                    raise Exception("风控")
                gen_time = res.get("data").get("seccode")["gen_time"]
                captcha_output = res.get("data").get("seccode")["captcha_output"]
                captcha_id = res.get("data").get("seccode")["captcha_id"]
                lot_number = res.get("data").get("seccode")["lot_number"]
                pass_token = res.get("data").get("seccode")["pass_token"]
                self.Request["X-TYCID"] = data["pow_sign"]
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
            response = self.session.get(url,
                                        headers=headers,
                                        params=params,
                                        proxies=self.Request["proxy"])
            print(response.text)
            if response.status_code == 200:
                res = json.loads(str(response.text).strip("(").strip(")"))
                token = res["data"]['token']
                id = str(res["data"]['userId'])
                self.create_cookie(id, self.Request["mobil"]["mobil"])
                logger.success("登录成功，同学开始愉快的玩耍吧！！")
                logger.info("【R】{}用户登录已成功！获取的sign：{}".format(id, token))
                self.Request["userid"] = id
                return token, data["pow_sign"]
        except Exception as e:
            logger.error(e)

    def get_cookie_csrf(self):
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
        # self.session.cookies.set("auth_token", token)
        url = "https://www.tianyancha.com/"
        self.session.get(url, headers=headers, proxies=self.Request["proxy"])
        self.Request["token"] = token
        self.Request["sign"] = sign

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
        self.session.cookies.set("tyc-user-phone", "%255B%252218587162714%2522%255D")
        # self.session.cookies.set("tyc-user-phone", "%255B%252218805000600%2522%252C%2522186%25208985%25208765%2522%252C%2522155%25208941%25205730%2522%252C%2522130%25200867%25206042%2522%255D")


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
        return proxies


    def main(self,mobil,flg,num):
            self.Request["ua"] = get()
            self.Request["proxy"] = self.proxy_list()
            self.Request["mobil"] = mobil
            self.get_cookie_csrf()
            timestamp = int(time.time() - random.randint(50000, 60000))
            self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758","{},{},{},{}".
                                     format(str(timestamp - random.randint(30000, 40000)),
                                            str(timestamp - random.randint(20000, 30000)),
                                            str(timestamp - random.randint(10000, 20000)),
                                            str(timestamp)))
            self.Request["sessionNo"] = "{:.8f}".format(time.time())
            self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758",str(int(time.time())))
            cookie_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
            print("======cookie_dict:",{
                "cookie_dict":cookie_dict,
                "ua":self.Request["ua"],
                "token":self.Request["token"],
                "sign":self.Request["sign"],
                "userid":self.Request["userid"],
                "sessionNo":self.Request["sessionNo"],
                "mobil":self.Request["mobil"]
            })
            cookie_data={
                "cookie_dict":cookie_dict,
                "ua": self.Request["ua"],
                "token":self.Request["token"],
                "sign":self.Request["sign"],
                "userid":self.Request["userid"],
                "sessionNo":self.Request["sessionNo"],
                "mobil":self.Request["mobil"]
            }
            for _ in range(num):
                if flg == 1:
                    self.conn.lpush("searchCookie",json.dumps(cookie_data))
                elif flg == 2:
                    self.local_T4_conn.lpush("NoMemeryCookie", json.dumps(cookie_data))
                elif flg==3:
                    self.local_T4_conn.lpush("sifaCookie", json.dumps(cookie_data))
                else:
                    self.conn.lpush("detailCookie", json.dumps(cookie_data))
            logger.success("已完成任务！！")



