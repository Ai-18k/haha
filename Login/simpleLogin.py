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

import hashlib
import json
import os
import random
import re
import time
import uuid
import ddddocr
import execjs
from loguru import logger
from feapder.network.user_agent import get
from lxml import etree
from curl_cffi import requests
from retrying import retry
from passVerify.geetest4_word import get_word_position

ocr = ddddocr.DdddOcr(det=False, ocr=False)
ocr1 = ddddocr.DdddOcr(beta=True)  # 切换为第二套ocr模型
ocr2 = ddddocr.DdddOcr(det=True)

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 构建JS文件路径
js_path = os.path.join(script_dir, "..", "RiskcontrolPass","jscode", "w_decode.js")
print(js_path)

class LoginModule:

    def __init__(self, mobil):
        self.session = requests.Session()
        self.Reqest = {}
        self.mobil = mobil
        self.finger=random.choices(["chrome99", "chrome100", "chrome101", "chrome104", "chrome107",
                       "chrome110", "chrome116", "chrome119", "chrome120", "edge99",
                       "edge101", "safari15_3",
                       "safari15_5", "safari17_0", "chrome99"])[0]
        print(self.finger)

    def get_1(self):
        try:
            self.get_cookie_csrf()
            uuid1 = uuid.uuid1()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                # "User-Agent": self.Reqest["ua"],
            }
            url = "https://gcaptcha4.geetest.com/load"
            params = {
                "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
                "challenge":uuid1,
                "client_type": "web",
                "lang": "zho"
            }
            response = self.session.get(url, headers=headers, params=params, proxies=self.Reqest["proxy"],impersonate=self.finger)
            if response.status_code == 200:
                cookies =response.cookies.get("captcha_v4_user")
                print(cookies)
                resp = json.loads(response.text.strip("(").strip(")"))
                type = resp["data"]['captcha_type']
                lot_number = resp["data"]["lot_number"]
                process_token = resp["data"]["process_token"]
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
                    q_list =resp["data"]['ques']
                    bytes_list = []
                    for index, img_url in enumerate(q_list):
                        tag = requests.get("https://static.geetest.com/" + img_url).content
                        bytes_list.append(tag)
                    imgs_url = "https://static.geetest.com/" + resp["data"]['imgs']
                    slide_bytes = requests.get(imgs_url).content
                    click_list = get_word_position(slide_bytes,bytes_list)
                    click_smark = []
                    for _word in click_list:
                        click_smark.append([round(int(_word[0]) * 100 / 3), round(int(_word[1]) * 50)])
                    logger.info(click_smark)
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
                    params_list["dis"] = dis
                    params_list["type"] = "slide"
                return params_list
        except Exception as e:
            logger.error(e)

    def re_jscodeV1(self):
        params_list = self.get_1()
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "no-cache",
            "origin": "https://www.qcc.com",
            "pragma": "no-cache",
            "referer": "https://www.qcc.com/",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "script",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        url = "https://static.geetest.com" + params_list["static_path"] + "/js/gcaptcha4.js"
        response =self.session.get(url, headers=headers,proxies=self.Reqest["proxy"],impersonate=self.finger)
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
        return {"par_param": res[0], "keys": res[1],"paramslist":params_list}


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
                "User-Agent": self.Reqest["ua"],
                "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", "
                             "\"Chromium\";v=\"123\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\""
            }
            url = "https://gcaptcha4.geetest.com/verify"
            res = self.re_jscodeV1()
            # jscode = open("../RiskcontrolPass/jscode/w_decode.js", encoding="utf-8").read()
            jscode = open(js_path, encoding="utf-8").read()
            data = execjs.compile(jscode).call("_fff", res["paramslist"], res["par_param"])
            params = {
                "captcha_id":"517df78b31ff1b8f841cd86fc0db9f3e",
                "client_type": "web",
                "lot_number": res["paramslist"]["lot_number"],
                "payload": res["paramslist"]["payload"],
                "process_token": res["paramslist"]["process_token"],
                "payload_protocol": "1",
                "pt": "1",
                "w": data["res"]
            }
            response = self.session.get(url,headers=headers,params=params,proxies=self.Reqest["proxy"],impersonate=self.finger)
            if response.status_code == 200:
                res = json.loads(str(response.text).strip("(").strip(")"))
                gen_time = res["data"]["seccode"]["gen_time"]
                captcha_output = res["data"]["seccode"]["captcha_output"]
                lot_number = res["data"]["seccode"]["lot_number"]
                pass_token = res["data"]["seccode"]["pass_token"]
                self.Reqest["lot_number"]=lot_number
                params_list1 = {
                    "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
                    "lot_number": lot_number,
                    "pass_token": pass_token,
                    "gen_time": gen_time,
                    "captcha_output": captcha_output,
                    "pow_sign": data["pow_sign"]
                }
                return params_list1
            else:
                logger.error(f"请求状态码:{response.status_code}")
        except Exception as e:
            logger.error("验证滑块异常:{}".format(e))

    @retry(wait_fixed=1000, stop_max_attempt_number=10)
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
            "X-TYCID": data["pow_sign"],
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", "
                         "\"Chromium\";v=\"114\", \"Google "
                         "Chrome\";v=\"114\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }
        url = "https://napi-huawei.tianyancha.com/next/web/cdloginv2_validatev2"
        params = {
            "mobile": self.mobil["mobil"],
            "cdpassword": hashlib.md5(
                self.mobil["pwd"].encode("utf-8")).hexdigest(),  # md5算法
            "loginway": "PL",
            "captcha_id": data["captcha_id"],
            "lot_number": data["lot_number"],
            "pass_token": data["pass_token"],
            "gen_time": data["gen_time"],
            "captcha_output": data["captcha_output"],
            "captcha_type": "pcLogin",
            "autoLogin": False}
        response = self.session.get(url, headers=headers, params=params,proxies=self.Reqest["proxy"],impersonate=self.finger)
        response.encoding = "utf-8"
        if response.status_code == 200:
            if "输入的手机号码与密码不匹配，推荐使用短信登录" not in response.text:
                res = json.loads(str(response.text).strip("(").strip(")"))
                print("登录响应结果----->:", res)
                if res["message"] == "":
                    token = res["data"]['token']
                    print(token)
                    logger.success(f"{self.mobil}:登录成功，同学开始愉快的玩耍吧！！")
                    self.Reqest["auth_token"] = token
                else:
                    logger.error(res)
            else:
                logger.error(f"{self.mobil}:账号密码错误!!")
                # with open("C:/Users/Administrator/Desktop/账号密码错误.txt", "a", encoding="utf-8") as f:
                #     f.write(self.mobil["mobil"] + "密码" + self.mobil["pwd"] + "\n")
                # local_VQ_conn.sadd("ErrorPwd", json.dumps(self.mobil))
                return False
        else:
            logger.error(f"{self.mobil}：账号异常无法登陆!!")
            with open("C:/Users/Administrator/Desktop/账号异常无法登陆.txt", "a", encoding="utf-8") as f:
                f.write(self.mobil["mobil"] + "密码" + self.mobil["pwd"] + "\n")
            return False


    def get_cookie_csrf(self):
        self.Reqest["proxy"]=None
        url = "https://www.tianyancha.com/"
        headers = {
            # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
            #           "image/avif,image/webp,image/apng,*/*;q=0.8,"
            #           "application/signed-exchange;v=b3;q=0.7",
            # "Accept-Language": "zh-CN,zh;q=0.9",
            # "Cache-Control": "no-cache",
            # "Connection": "keep-alive",
            # "DNT": "1",
            # "Pragma": "no-cache",
            # "Referer": "https://www.tianyancha.com/",
            # "Sec-Fetch-Dest": "document",
            # "Sec-Fetch-Mode": "navigate",
            # "Sec-Fetch-Site": "same-origin",
            # "Sec-Fetch-User": "?1",
            # "Upgrade-Insecure-Requests": "1",
            # "User-Agent": self.Reqest["ua"],
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            # "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
            #              "Chrome\";v=\"114\"",
            # "sec-ch-ua-mobile": "?0",
            # "sec-ch-ua-platform": "\"Windows\""
        }
        response = self.session.get(url, headers=headers, proxies=self.Reqest["proxy"],impersonate=self.finger)
        if response.status_code == 200:
            self.Reqest["CUID"] = self.session.cookies.get("CUID")
            self.Reqest["TYCID"] =self.session.cookies.get("TYCID")
            return self.session

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

    def demo1(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
        }
        cookies = {
            "CUID": self.Reqest["CUID"],
            "TYCID":self.Reqest["TYCID"],
            "auth_token": self.Reqest["auth_token"]
        }
        url = "https://www.tianyancha.com/human/2277807374-c150041670"
        response = requests.get(url, headers=headers, cookies=cookies,impersonate=self.finger)
        print(response)
        html = etree.HTML(response.text)
        json_date = json.loads(html.xpath('//script[@id="__NEXT_DATA__"]/text()')[0])
        gudong = json_date["props"]["pageProps"]["dehydratedState"]["queries"][7]["state"]["data"]["data"]["holderList"]
        faren = json_date["props"]["pageProps"]["dehydratedState"]["queries"][7]["state"]["data"]["data"]["legalList"]
        print(gudong)
        print(faren)


    def paramdata(self):
        pass


    def demo2(self):
        headers = {"Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/json",
                    "version": "TYC-Web",
                    "eventId": "i246",
                    "pm": "451",
                    "spm": "i246",
                    "page_id": "SearchResult",
                    "X-TYCID": self.Reqest["TYCID"],
                    "X-AUTH-TOKEN":self.Reqest["auth_token"]}
        url = "https://capi.tianyancha.com/cloud-company-background/companyV2/dim/historyHolder"
        params = {
            "_": str(int(time.time()*1000)),
        }
        data = {
            "gid": "22822",
            "pageSize": 50,
            "pageNum": 1,
            "historyType": 2,
            "benefitSharesType": 1,
            "_unUseParam": 1,
            "percentLevel": "-100",
            "keyword": ""
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, params=params, data=data)
        print(response)
        companyName=response.json()["data"]["companyName"]
        datas=response.json()["data"]["result"]
        shareholderInfoHistory=[]
        for data in datas:
            item=dict()
            item["shareholderName"]=data['shareHolderName']
            item["shareholderRatio"]=data["percent"]
            item["avatarAddress"]=data["logo"]
            item["shareholderType"]=data["shareHolderTypeOnPage"]
            item["subscribedCapitalContribution"]=data["totalCapital"]
            item["dateSubscribedCapitalContribution"]=data["investmentStartTime"]
            item["dateInitialShareholding"]=data["investmentEndTime"]
            item["companyName"]=companyName
            item["uniqueCode"]=data["shareHolderNameId"]
            shareholderInfoHistory.append(item)
        print(shareholderInfoHistory)

    def demo3(self):
        headers = {"Accept": "application/json, text/plain, */*",
                   "Content-Type": "application/json",
                   "version": "TYC-Web",
                   "eventId": "i246",
                   "pm": "451",
                   "spm": "i246",
                   "page_id": "SearchResult",
                   "X-TYCID": self.Reqest["TYCID"],
                   "X-AUTH-TOKEN": self.Reqest["auth_token"]}
        url = "https://capi.tianyancha.com/cloud-company-background/companyV2/dim/holder/latest/announcement"
        params = {
            "_": str(int(time.time()*1000)),
        }
        data = {
            "gid": "22822",
            "pageSize": 50,
            "pageNum": 1,
            "historyType": None,
            "benefitSharesType": 1,
            "_unUseParam": 0
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, params=params, data=data)
        print(response)
        companyName = "北京百度网讯科技有限公司"
        datas = response.json()["data"]["result"]
        shareholderInfo = []
        for data in datas:
            item = dict()
            item["shareholderName"] = data['shareHolderName']
            item["shareholderRatio"] = data["percent"]
            item["avatarAddress"] = data["logo"]
            item["shareholderType"] = data["shareHolderTypeOnPage"]
            item["subscribedCapitalContribution"] = data["totalCapital"]
            item["dateSubscribedCapitalContribution"] = data["investmentStartTime"]
            item["dateInitialShareholding"] = data["investmentEndTime"] if data["investmentEndTime"] else data["latestCapitalTime"]
            item["companyName"] = companyName
            item["uniqueCode"] = data["shareHolderNameId"]
            shareholderInfo.append(item)
        print(shareholderInfo)


    def main(self):
        self.Reqest["proxy"] =self.proxy_list()
        self.Reqest["ua"] = get()
        self.get_3()
        return self.Reqest
        # self.demo1()
        # self.demo2()
        # self.demo3()
        # if self.get_3():
        #     timestamp = int(time.time() - random.randint(30000, 40000))
        #     self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758", "{},{},{},{}".
        #                              format(str(timestamp - random.randint(30000, 40000)),
        #         str(timestamp - random.randint(20000, 30000)),
        #         str(timestamp - random.randint(10000, 20000)),
        #         str(timestamp)))
        #     self.Reqest["sessionNo"] = "{:.8f}".format(time.time())
        #     self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758", str(int(time.time()) - 4000))
        #     cookie_dict = requests.utils.dict_from_cookiejar(self.session.cookies)
        #     print("======cookie_dict:", {
        #         "cookie_dict": cookie_dict,
        #         "ua": self.Reqest["ua"],
        #         "token": self.Reqest["auth_token"],
        #         "sign": self.Reqest["sign"],
        #         "userid": self.Reqest["userid"],
        #         "sessionNo": self.Reqest["sessionNo"],
        #         "mobil": self.mobil
        #     })
        #     cookie_data = {
        #         "cookie_dict": cookie_dict,
        #         "ua": self.Reqest["ua"],
        #         "token": self.Reqest["auth_token"],
        #         "sign": self.Reqest["sign"],
        #         "userid": self.Reqest["userid"],
        #         "sessionNo": self.Reqest["sessionNo"],
        #         "mobil": self.mobil
        #     }
        #     for i in range(4):
        #         self.local_conn.lpush("searchCookie", json.dumps(cookie_data))
        # else:
        #     return False


if __name__ == '__main__':
    mobil ={"mobil": "13880895836", "pwd": "why758124"}
    # mobil ={"mobil": "17773164326", "pwd": "lisuqin19891016"}
    LoginModule(mobil).main()
