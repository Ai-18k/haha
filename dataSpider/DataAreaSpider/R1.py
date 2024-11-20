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
import random
from concurrent.futures import ThreadPoolExecutor
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
from pymongo import MongoClient
from retrying import retry


class SuccessCODE():

    def __init__(self):
        self.client = MongoClient(host='192.168.5.167', port=27017)
        self.client_01 = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",
                                     authSource="admin")
        # self.conn = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123", socket_connect_timeout=170)
        # self.local_conn = redis.Redis(host='120.0.0.1', port=7980, db=0, password="qwe!@#SDF345788",socket_connect_timeout=70)
        self.local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=70)
        self.local_T4_conn = redis.Redis(host='192.168.5.87', port=7933, db=0, password="fer@nhaweif576KUG",socket_connect_timeout=70)
        self.session = requests.session()
        self.coll = self.client["hubei"]["company_id"]
        self.coll_1 = self.client_01["hubei"]["company_id"]
        self.Request={}
        self.filter = "hubei:filter:company_id"
        self.filter_params = "hubei:filter:params"
        self.com_id = "hubei:company_id"
        self.params="hubei:params"

    def get_1(self):
        headers = {
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "DNT": "1",
                "Pragma": "no-cache",
                "Referer": "https://www.geetest.com/",
                "Sec-Fetch-Dest": "script",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "same-site",
                "User-Agent":self.Request["ua"],
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
            static_path=res.get("data").get("static_path")
            if isinstance(pow_detail,dict):
                pow_detail = [pow_detail[i] for i in pow_detail]
            payload = res.get("data").get("payload")
            params_list = {
                    "captcha_id": params["captcha_id"],
                    "lot_number": lot_number,
                    "process_token": process_token,
                    "pow_detail": pow_detail,
                    "payload": payload,
                    "cookies": cookies,
                    "static_path":static_path
                    }
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
            "User-Agent": self.Reqest["ua"],
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
        str_code += "return " + matche_05.group() + "};"
        res = execjs.compile(str_code).call("get_param")
        return {"par_param": res, "par_data": params_list}


    def get_2(self):
        try:
            p = self.get_1()
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
            par=self.re_js_code()
            logger.info(f"》》》》》》正在获取js参数............")
            data = execjs.compile(open("../../RiskcontrolPass/jscode/w_decode.js",encoding="utf-8").read()).call("_fff",p,par)
            cookies = {
                    "captcha_v4_user": p["cookies"]
                    }
            params = {
                    "captcha_id": p["captcha_id"],
                    "client_type": "web",
                    "lot_number": p["lot_number"],
                    "payload": p["payload"],
                    "process_token": p["process_token"],
                    "payload_protocol": "1",
                    "pt": "1",
                    "w": data["res"]
                    }
            response = self.session.get(url,
                    headers=headers,
                    cookies=cookies,
                    params=params,
                    proxies=self.Request["proxy"])
            if response.status_code == 200:
                res = json.loads(str(response.text).strip("(").strip(")"))
                print(res)
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
                time.sleep(2)
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
                elif res["message"]=="账号存在风险，暂不能操作":
                    self.local_T4_conn.lpush("ErrorMobil", json.dumps(self.Request["mobil"]))
                    self.local_T4_conn.lrem("testUser", 1, json.dumps(self.Request["mobil"]))
                    self.main()
                    return
                else:
                    logger.error(f"登录异常: {res} ")
        except TypeError as e:

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
        # else:
        #     raise Exception("请求代理")

    def next_page(self,info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-tempest/web/searchCompanyV3"
                headers = {
                    "Host": "capi.tianyancha.com",
                    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                                 "Chrome\";v=\"114\"",
                    "sec-ch-ua-platform": "\"Windows\"",
                    "X-TYCID": self.Request["sign"],
                    "DNT": "1",
                    "sec-ch-ua-mobile": "?0",
                    "User-Agent": self.Request["ua"],
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/plain, */*",
                    "X-AUTH-TOKEN": self.Request["token"],
                    "version": "TYC-Web",
                    "Origin": "https://www.tianyancha.com",
                    "Sec-Fetch-Site": "same-site",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Referer": "https://www.tianyancha.com/",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }
                params = {"_": str(int(time.time() * 1000))}
                data = {
                    "word": "$",
                    "sortType": "0",
                    "pageSize": 20,
                    "referer": "search",
                    "type": "tail",
                    "key": "",
                    "orgType": info["orgType"],
                    "cacheCode": info['areaCode'],
                    "sessionNo": self.Request["sessionNo"],
                    "customAreaCode": info['areaCode'],
                    "estiblishTimeStart": str(info["new_day"]),
                    "estiblishTimeEnd": str(info["next_day"]),
                    "pageNum": page
                }
                str_data = json.dumps(data, separators=(',', ':'))
                response = self.session.post(url,headers=headers,params=params,data=str_data)
                logger.info(info)
                logger.info(self.Request["mobil"])
                logger.info(response.status_code)
                if response.status_code == 200:
                    if response.json()["errorCode"] == "":
                        if "data" in response.json():
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
                                    self.coll_1.insert_one(info)
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
                            mobil = self.local_T4_conn.lpop("testUser")
                            self.local_T4_conn.rpush("testUser", mobil)
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
                        mobil = self.local_T4_conn.lpop("testUser")
                        self.local_T4_conn.rpush("testUser", mobil)
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
                        self.local_T4_conn.lpush("ErrorMobil", json.dumps(self.Request["mobil"]))
                        self.local_T4_conn.lrem("testUser", 1, json.dumps(self.Request["mobil"]))
                        mobil = self.local_T4_conn.lpop("testUser")
                        self.local_T4_conn.rpush("testUser", mobil)
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
                        time.sleep(30)
                        self.next_page(info,page)
                        break
                else:
                    print("有风控?")
                page+=1
            except:
                self.local_conn.lpush("hubei:fail_params",json.dumps(info))


    def main(self):
        with ThreadPoolExecutor(2) as f:
            self.Request["ua"] = get()
            self.Request["proxy"] = self.proxy_list()
            mobil = self.local_T4_conn.lpop("testUser")
            self.local_T4_conn.rpush("testUser", mobil)
            self.Request["mobil"] = json.loads(mobil)
            self.get_cookie_csrf()
            timestamp = int(time.time() - random.randint(50000, 60000))
            self.session.cookies.set("Hm_lvt_e92c8d65d92d534b0fc290df538b4758","{},{},{},{}".
                                     format(str(timestamp - random.randint(30000, 40000)),
                                            str(timestamp - random.randint(20000, 30000)),
                                            str(timestamp - random.randint(10000, 20000)),
                                            str(timestamp)))
            self.Request["sessionNo"] = "{:.8f}".format(time.time())
            self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758",str(int(time.time())))
            _=1
            futures=[]
            while True:
                try:
                    if _ % 900==0:
                        self.Request["ua"]=get()
                        self.Request["proxy"]=self.proxy_list()
                        mobil = self.local_T4_conn.lpop("testUser")
                        self.local_T4_conn.rpush("testUser", mobil)
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
                        info_str = ",".join([str(info[i]) for i in info.keys()])
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
                    #     futures.clear()
                    _ += 1
                    logger.info(f"。。。。。。。。。。。。这是第 {_} 家公司")
                except redis.exceptions.TimeoutError as e:
                    logger.error(e)
                    self.main()
                    return
            # for future in futures:
            #     future.result()


if __name__ == '__main__':
    sc = SuccessCODE()
    sc.main()
