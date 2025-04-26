import json
import math
import random
import time
from concurrent.futures import ThreadPoolExecutor
import datetime
from redis import Redis
from loguru import logger
from pymongo import MongoClient, ASCENDING, errors
from retrying import retry
from PikaUse import mongoToMQ
import requests
from config import checkconfig


class NoMemerySpider:

    def __init__(self,area):
        self.config = checkconfig(area)
        self.session = requests.session()
        self.local_conn = Redis("192.168.5.%s" % self.config["fAddr"][0],
                                      self.config["fAddr"][1],
                                      self.config["fAddr"][2],
                                      self.config["fAddr"][3],
                                      socket_connect_timeout=1170)
        self.local_VQ_conn =Redis("192.168.5.%s" % self.config["uAddr"][0],
                                         self.config["uAddr"][1],
                                         self.config["uAddr"][2],
                                         self.config["uAddr"][3],
                                         socket_connect_timeout=1155)
        self.client_01 = MongoClient(host="139.9.70.%s"%self.config["servSAddr"][0],
                                     port=self.config["servSAddr"][1],
                                     username=self.config["servSAddr"][2],
                                     password=self.config["servSAddr"][3],
                                     authSource=self.config["servSAddr"][4])
        self.client = MongoClient("192.168.5.%s"%self.config['localSAddr'][0],
                                  self.config['localSAddr'][1])
        self.cli_5 = self.client[self.config["rkey"]]["company_id"]
        self.coll = self.client_01[self.config["rkey"]]['商标信息']
        self.coll1 = self.client_01[self.config["rkey"]]['作品著作权']
        self.coll2 = self.client_01[self.config["rkey"]]['电信许可']
        self.coll3 = self.client_01[self.config["rkey"]]['软著著作权']
        self.coll4 = self.client_01[self.config["rkey"]]['行政许可']
        self.coll5 = self.client_01[self.config["rkey"]]['资质证书']

        self.cli=self.client[self.config["rkey"]]['商标信息']
        self.cli1=self.client[self.config["rkey"]]['作品著作权']
        self.cli2=self.client[self.config["rkey"]]['电信许可']
        self.cli3=self.client[self.config["rkey"]]['软著著作权']
        self.cli4=self.client[self.config["rkey"]]['行政许可']
        self.cli5=self.client[self.config["rkey"]]['资质证书']

        self.c_fail = self.client[self.config["rkey"]]["fails_商标信息"]
        # self.c_fail.create_index([('company', ASCENDING)], unique=True)

        self.c_fail1 = self.client[self.config["rkey"]]["fails_作品著作权"]
        self.c_fail1.create_index([('company', ASCENDING)], unique=True)

        self.c_fail2 = self.client[self.config["rkey"]]["fails_电信许可"]
        # self.c_fail2.create_index([('company', ASCENDING)], unique=True)

        self.c_fail3 = self.client[self.config["rkey"]]["fails_软著著作权"]
        # self.c_fail3.create_index([('company', ASCENDING)], unique=True)

        self.c_fail4 = self.client[self.config["rkey"]]["fails_行政许可"]
        # self.c_fail4.create_index([('company', ASCENDING)], unique=True)

        self.c_fail5 = self.client[self.config["rkey"]]["fails_资质证书"]
        # self.c_fail5.create_index([('company', ASCENDING)], unique=True)

        self.sbxx_list=list()   #4
        self.zpzzq_list=list()  #5
        self.rzzzq_list=list()  #6
        self.f_map = {"4": self.sbxx_list, "5": self.zpzzq_list,"6": self.rzzzq_list}
        self.Request=dict()
        self.headers=dict()
        self.area_key = self.config["rkey"] + ":company_id"
        self.sbxx_filter_key = self.config["rkey"] + ":filter:sbxx"
        self.zpzzq_filter_key = self.config["rkey"] + ":filter:zpzzq"
        self.rzzzq_filter_key = self.config["rkey"] + ":filter:rzzzq"
        self.zzzs_filter_key = self.config["rkey"] + ":filter:zzzs"
        self.xzxk_filter_key = self.config["rkey"] + ":filter:xzxk"
        self.dxxk_filter_key = self.config["rkey"] + ":filter:dxxk"

    @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def proxy_list(self):
        if self.config["proxy"]:
            # global l
            # l = random.randint(1, 6)
            # 隧道域名:端口号
            tunnel = self.config["proxy"][2]
            # 用户名密码方式
            username = self.config["proxy"][0]
            password = "%s:%d" % (self.config["proxy"][1],self.Request["pchannel"])
            proxies = {
                "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
                "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
            }
            try:
                resp = requests.get("https://myip.ipip.net", proxies=proxies,timeout=(4,10))
                if resp.status_code == 200:
                    print(resp.text)
                    return proxies
                else:
                    return None
            except requests.Timeout as e:
                logger.error(e)
                return None
            except requests.ConnectionError as e:
                logger.error(e)
                raise "代理异常"
        else:
            return None

    # 商标信息    已测试
    def sbxx(self,info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-intellectual-property" \
                      "/intellectualProperty/trademarkList"
                params = {
                    "_": str(int(time.time() * 1000))
                }
                data = {
                    "id": info["id"],
                    "ps": 10,
                    "pn": page,
                    "int_cls": "-100",
                    "status": "-100",
                    "app_year": "-100",
                    "regYear": "-100",
                    "searchType": "-100",
                    "category": "-100",
                    "fullSearchText": "",
                    "sortField": "",
                    "sortType": "-100"
                }
                data = json.dumps(data, separators=(',', ':'))
                response = requests.post(url, headers=self.headers, params=params, data=data,proxies=self.Request["proxy"],timeout=(4,10))
                data=response.json()
                print(data)
                if data["state"] == "ok":
                    if data['data']:
                        num = math.ceil(int(data['data']['viewtotal']) / 10) if data['data']['viewtotal'] else 0
                        logger.info(f'这个链接共{num}页数据')
                        logger.info(f'当前是第{page}页')
                    else:
                        break
                    if page > num:
                        break
                    if response.status_code == 200:
                        for item in data['data']['items']:
                            item["companyName"] = info["company"]
                            self.coll.insert_one(item)
                            data = {
                                'relationCompanyName': item['companyName'],
                                'propertyType': '商标',
                                'propertyTitle': item['tmName'],
                                'propertyNum': item['regNo'],
                                'filingDate': item['eventTime'],
                                'infoType': item['intCls'],
                                'infoStatus': item['status'],
                                'gainDate': item['pubDate'],
                                'content': '',
                                'sbImageUrl': item['tmPic'],
                                'zlInventor': '',
                                'zlOpenNum': '',
                                'rzSimpleName': '',
                                'rzVersionsNum': '',
                                'zpCompletionDate': '',
                            }
                            self.cli.insert_one(data)
                            if "_id" in data:
                                del data["_id"]
                            self.send_data(4,data)
                            logger.info(f"第 {page} 页数据！！")
                            logger.success(f"【*】商标 数据保存成功:{data}!!")
                        page += 1
                else:
                    while True:
                        res = self.local_VQ_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.Request["proxy"] = self.proxy_list()
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["cookie_dict"]["TYCID"],
                                "DNT": "1",
                                "sec-ch-ua-mobile": "?0",
                                "User-Agent": self.Request['ua'],
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/plain, */*",
                                "X-AUTH-TOKEN": self.Request["token"],
                                "version": "TYC-Web",
                                "Origin": "https://www.tianyancha.com",
                                "Sec-Fetch-Site": "same-site",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Dest": "empty",
                                "Referer": "https://www.tianyancha.com/",
                                "Accept-Language": "zh-CN,zh;q=0.9"}
                            self.sbxx(info, page)
                            break
                    break
            except Exception as e:
                logger.error(e)
                info["page"]=page
                if "_id" in info:
                    del info["_id"]
                self.Request["pchannel"]=random.randint(1,6)
                self.Request["proxy"] = self.proxy_list()
                try:
                    self.c_fail.insert_one(info)
                    print("数据插入成功！")
                except errors.DuplicateKeyError:
                    print("数据已存在，插入失败！")
        self.local_conn.sadd(self.sbxx_filter_key, info["company"])

    # 作品著作权    已测试
    def zpzzq(self,info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-intellectual-property/intellectualProperty/worksCopyrightListNew"
                params = {
                    "_": str(int(time.time() * 1000)),
                    "gid": info["id"],
                    "pageSize": "10",
                    "pageNum": page,
                    "category": "-100",
                    "registrationYear": "-100",
                    "fullSearchText": ""
                }
                response = requests.get(url,headers=self.headers,params=params,proxies=self.Request["proxy"],timeout=(4,10))
                data=response.json()
                print(data)
                if data["state"] == "ok":
                    num = math.ceil(int(data['data']['count']) / 10) if data['data']['count'] else 0
                    logger.info(f'这个链接共{num}页数据')
                    logger.info(f'当前是第{page}页')
                    if page > num:
                        break
                    if response.status_code == 200:
                        for item in data['data']['resultList']:
                            item["companyName"] = info["company"]
                            self.coll1.insert_one(item)
                            zpCompletionDate = item['publishtime']
                            if zpCompletionDate:
                                zpCompletionDate = ''
                            else:
                                zpCompletionDate = zpCompletionDate
                            data = {
                                'relationCompanyName': item['companyName'],
                                'propertyType': '作品著作权',
                                'propertyTitle': item['fullname'],
                                'propertyNum': item['regnum'],
                                'filingDate': item['regtime'],
                                'infoType': item['type'],
                                'infoStatus': '',
                                'gainDate': item['publishtime'],
                                'content': '',
                                'sbImageUrl': '',
                                'zlInventor': '',
                                'zlOpenNum': '',
                                'rzSimpleName': '',
                                'rzVersionsNum': '',
                                'zpCompletionDate': zpCompletionDate,
                            }
                            self.cli1.insert_one(data)
                            if "_id" in data:
                                del data["_id"]
                            self.send_data(4, data)
                            logger.success(f"【*】作品著作权 数据保存成功:{data}!!")
                        page += 1
                else:
                    while True:
                        res = self.local_VQ_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.Request["proxy"] = self.proxy_list()
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["cookie_dict"]["TYCID"],
                                "DNT": "1",
                                "sec-ch-ua-mobile": "?0",
                                "User-Agent": self.Request['ua'],
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/plain, */*",
                                "X-AUTH-TOKEN": self.Request["token"],
                                "version": "TYC-Web",
                                "Origin": "https://www.tianyancha.com",
                                "Sec-Fetch-Site": "same-site",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Dest": "empty",
                                "Referer": "https://www.tianyancha.com/",
                                "Accept-Language": "zh-CN,zh;q=0.9"}
                            self.zpzzq(info,page)
                            break
                    break
            except Exception as e:
                logger.error(e)
                info["page"] = page
                if "_id" in info:
                    del info["_id"]
                self.Request["pchannel"] = random.randint(1, 6)
                self.Request["proxy"] = self.proxy_list()
                try:
                    self.c_fail1.insert_one(info)
                    print("数据插入成功！")
                except errors.DuplicateKeyError:
                    print("数据已存在，插入失败！")
        self.local_conn.sadd(self.zpzzq_filter_key, info["company"])

    # 软著著作权    已测试
    def rzzzq(self,info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-intellectual-property" \
                      "/intellectualProperty/softwareCopyrightListV2"
                params = {
                    "_": str(int(time.time() * 1000)),
                    "id": info["id"],
                    "pageSize": "10",
                    "pageNum": page,
                    "regYear": "-100",
                    "fullSearchText": ""
                }
                response = requests.get(url,headers=self.headers,params=params,proxies=self.Request["proxy"],timeout=(4,10))
                data = response.json()
                if data["state"] == "ok":
                    print(data)
                    if data['data'] is not None:
                        num = math.ceil(int(data['data']['total']) / 10) if data['data']['total'] else 0
                        logger.info(f'这个链接共{num}页数据')
                        logger.info(f'当前是第{page}页')
                    else:
                        break
                    if page > num :
                        break
                    data=response.json()
                    if response.status_code == 200:
                        for item in data['data']['items']:
                            item["companyName"] = info["company"]
                            self.coll3.insert_one(item)
                            # 将毫秒时间戳转换为秒时间戳
                            try:
                                filingDate =datetime.datetime.fromtimestamp(item['regtime']/1000).strftime('%Y-%m-%d') if item['regtime'] else ""
                            except:
                                filingDate =None
                            try:
                                gainDate = datetime.datetime.fromtimestamp(item['publishtime'] / 1000).strftime('%Y-%m-%d') if \
                                item['publishtime'] else ""
                            except:
                                gainDate =None
                            data = {
                                'relationCompanyName': item['companyName'],
                                'propertyType': '软著著作权',
                                'propertyTitle': item['fullname'],
                                'propertyNum': item['regnum'],
                                'filingDate': filingDate,
                                'infoType': '',
                                'infoStatus': '',
                                'gainDate': gainDate,
                                'content': '',
                                'sbImageUrl': '',
                                'zlInventor': '',
                                'zlOpenNum': '',
                                'rzSimpleName': item['simplename'],
                                'rzVersionsNum': item['version'],
                                'zpCompletionDate': '',
                            }
                            self.cli3.insert_one(data)
                            if "_id" in data:
                                del data["_id"]
                            self.send_data(4,data)
                            logger.success(f"【*】软件著作权 数据保存成功:{data}!!")
                        page += 1
                else:
                    while True:
                        res = self.local_VQ_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.Request["proxy"] = self.proxy_list()
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["cookie_dict"]["TYCID"],
                                "DNT": "1",
                                "sec-ch-ua-mobile": "?0",
                                "User-Agent": self.Request['ua'],
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/plain, */*",
                                "X-AUTH-TOKEN": self.Request["token"],
                                "version": "TYC-Web",
                                "Origin": "https://www.tianyancha.com",
                                "Sec-Fetch-Site": "same-site",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Dest": "empty",
                                "Referer": "https://www.tianyancha.com/",
                                "Accept-Language": "zh-CN,zh;q=0.9"}
                            self.rzzzq(info,page)
                            break
                    break
            except Exception as e:
                logger.error(e)
                info["page"] = page
                if "_id" in info:
                    del info["_id"]
                self.Request["pchannel"] = random.randint(1, 6)
                self.Request["proxy"] = self.proxy_list()
                try:
                    self.c_fail3.insert_one(info)
                    print("数据插入成功！")
                except errors.DuplicateKeyError:
                    print("数据已存在，插入失败！")
        self.local_conn.sadd(self.rzzzq_filter_key, info["company"])

    # 资质证书    已测试
    def zzzs(self,info,page):
        while True:
            try:
                url = 'https://capi.tianyancha.com/cloud-business-state/certificate/list'
                params = {
                    "_": str(int(time.time() * 1000)),
                    'graphId': info["id"],
                    'pageSize': '10',
                    'pageNum': page,
                    'type': '',
                }
                response = requests.get(url, params=params,headers=self.headers,proxies=self.Request["proxy"],timeout=(4,10))
                data=response.json()
                print(data)
                if data["state"] =="ok":
                    num = math.ceil(int(data['data']['count']) / 10) if data['data'][
                        'count'] else 0
                    logger.info(f'这个链接共{num}页数据')
                    logger.info(f'当前是第{page}页')
                    if page > num:
                        break
                    if response.status_code == 200:
                        for item in data['data']['resultList']:
                            item["companyName"] = info["company"]
                            self.coll5.insert_one(item)
                            json_data = {
                                'relationCompanyName': item['companyName'],
                                'startTime': item['startDate'],
                                'endTime': item['endDate'],
                                'certificateNumber': item['certNo'],
                                'certificateType': item['certificateName'],
                            }
                            self.cli5.insert_one(json_data)
                            if "_id" in json_data:
                                del json_data["_id"]
                            self.send_data(6,json_data)
                            logger.success(f"【*】资质证书 数据保存成功:{json_data}!!")
                        page += 1
                else:
                    while True:
                        res = self.local_VQ_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.Request["proxy"] = self.proxy_list()
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["cookie_dict"]["TYCID"],
                                "DNT": "1",
                                "sec-ch-ua-mobile": "?0",
                                "User-Agent": self.Request['ua'],
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/plain, */*",
                                "X-AUTH-TOKEN": self.Request["token"],
                                "version": "TYC-Web",
                                "Origin": "https://www.tianyancha.com",
                                "Sec-Fetch-Site": "same-site",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Dest": "empty",
                                "Referer": "https://www.tianyancha.com/",
                                "Accept-Language": "zh-CN,zh;q=0.9"}
                            self.zzzs(info,page)
                            break
                    break
            except Exception as e:
                logger.error(e)
                info["page"]=page
                if "_id" in info:
                    del info["_id"]
                self.Request["pchannel"] = random.randint(1, 6)
                self.Request["proxy"] = self.proxy_list()
                try:
                    self.c_fail5.insert_one(info)
                    print("数据插入成功！")
                except errors.DuplicateKeyError:
                    print("数据已存在，插入失败！")
        self.local_conn.sadd(self.zzzs_filter_key, info["company"])


    # 行政许可    已测试
    def xzxk(self,info,page):
        while True:
            try:
                url = 'https://capi.tianyancha.com/cloud-business-state/license/licenseList'
                params = {
                    '_': str(int(time.time() * 1000)),
                    'gid': info["id"],
                    'pageNum': page,
                    'pageSize': '10',
                }
                response = requests.get(url, params=params,headers=self.headers,proxies=self.Request["proxy"],timeout=(4,10))
                data = response.json()
                print(data)
                if data["state"] == "ok":
                    num = math.ceil(int(data['data']['totalCount']) / 10) if data['data']['totalCount'] else 0
                    logger.info(f'这个链接共{num}页数据')
                    logger.info(f'当前是第{page}页')
                    if page > num:
                        break
                    if response.status_code == 200:
                        for item in data['data']['list']:
                            item["companyName"] = info["company"]
                            self.coll4.insert_one(item)
                            data = {
                                'relationCompanyName': item['companyName'],
                                'licenceType': '行政许可',
                                'startTime': item['fromDate'],
                                'endTime': item['endDate'],
                                'licenceNumber': item['licenceNumber'],
                                'licenceName': item['licenceName'],
                                'licenceUnit': item['licenceDepartment'],
                                'licenceContent': item['licenceContent'],
                                'isValid': '',
                            }
                            self.cli4.insert_one(data)
                            if "_id" in data:
                                del data["_id"]
                            self.send_data(5,data)
                            logger.success(f"【*】资质证书 数据保存成功:{data}!!")
                        page += 1
                else:
                    while True:
                        res = self.local_VQ_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.Request["proxy"] = self.proxy_list()
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["cookie_dict"]["TYCID"],
                                "DNT": "1",
                                "sec-ch-ua-mobile": "?0",
                                "User-Agent": self.Request['ua'],
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/plain, */*",
                                "X-AUTH-TOKEN": self.Request["token"],
                                "version": "TYC-Web",
                                "Origin": "https://www.tianyancha.com",
                                "Sec-Fetch-Site": "same-site",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Dest": "empty",
                                "Referer": "https://www.tianyancha.com/",
                                "Accept-Language": "zh-CN,zh;q=0.9"}
                            self.xzxk(info, page)
                            break
                    break
            except Exception as e:
                logger.error(e)
                info["page"] = page
                if "_id" in info:
                    del info["_id"]
                self.Request["pchannel"] = random.randint(1, 6)
                self.Request["proxy"] = self.proxy_list()
                try:
                    self.c_fail4.insert_one(info)
                    print("数据插入成功！")
                except errors.DuplicateKeyError:
                    print("数据已存在，插入失败！")
        self.local_conn.sadd(self.xzxk_filter_key, info["company"])


    # 电信许可  已测试
    def dxxk(self,info,page):
        while True:
            try:
                url = 'https://capi.tianyancha.com/cloud-business-state/telCommunicationLicense/list'
                params = {
                    '_': str(int(time.time() * 1000)),
                    'id': info["id"],
                    'pageSize': '10',
                    'pageNum': page,
                }
                response = requests.get(url,params=params,headers=self.headers,proxies=self.Request["proxy"],timeout=(4,10))
                data=response.json()
                print(data)
                if data["state"] == "ok":
                    num = math.ceil(int(data['data']['total']) / 10) if data['data']['total'] else 0
                    logger.info(f'这个链接共{num}页数据')
                    logger.info(f'当前是第{page}页')
                    if page > num:
                        break
                    if response.status_code == 200:
                        for item in data['data']['items']:
                            self.coll2.insert_one(item)
                            json_data = {
                                'relationCompanyName': info["company"],
                                'licenceType': '电信许可',
                                'startTime': '',
                                'endTime': '',
                                'licenceNumber': item['licenseNumber'],
                                'licenceName': '',
                                'licenceUnit': '',
                                'licenceContent': item['businessScope'],
                                'isValid': item['isAvailable'],
                            }
                            self.cli2.insert_one(json_data)
                            if "_id" in json_data:
                                del json_data["_id"]
                            self.send_data(5,json_data)
                            logger.success(f"【*】电信许可 数据保存成功:{json_data}!!")
                        page += 1
                else:
                    while True:
                        res = self.local_VQ_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.Request["proxy"] = self.proxy_list()
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["cookie_dict"]["TYCID"],
                                "DNT": "1",
                                "sec-ch-ua-mobile": "?0",
                                "User-Agent": self.Request['ua'],
                                "Content-Type": "application/json",
                                "Accept": "application/json, text/plain, */*",
                                "X-AUTH-TOKEN": self.Request["token"],
                                "version": "TYC-Web",
                                "Origin": "https://www.tianyancha.com",
                                "Sec-Fetch-Site": "same-site",
                                "Sec-Fetch-Mode": "cors",
                                "Sec-Fetch-Dest": "empty",
                                "Referer": "https://www.tianyancha.com/",
                                "Accept-Language": "zh-CN,zh;q=0.9"}
                            self.dxxk(info, page)
                            break
                    break
            except Exception as e:
                logger.error(e)
                info["page"] = page
                if "_id" in info:
                    del info["_id"]
                self.Request["pchannel"] = random.randint(1, 6)
                self.Request["proxy"] = self.proxy_list()
                try:
                    self.c_fail2.insert_one(info)
                    print("数据插入成功！")
                except errors.DuplicateKeyError:
                    print("数据已存在，插入失败！")
        self.local_conn.sadd(self.dxxk_filter_key, info["company"])


    def send_data(self,flg,item):
        print(f">>>>>>> %s 记录打点: %d " % (flg, len(self.f_map[str(flg)])))
        self.f_map[str(flg)].append(item)
        if len(self.f_map[str(flg)]) >= 20:
            logger.info(self.f_map[str(flg)])
            mongoToMQ(flg, self.f_map[str(flg)])
            logger.success(f"【*】发送成功：{self.f_map[str(flg)]}")
            self.f_map[str(flg)].clear()


    def main(self):
        while True:
            res = self.local_VQ_conn.lpop("NoMemeryCookie")
            if res is None:
                print(">>>>>>>>>>>>>>获取cookie信息..........")
                time.sleep(0.5)
            else:
                self.Request = json.loads(res.decode("utf-8"))
                print(self.Request)
                self.Request["proxy"] = self.proxy_list()
                self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                self.headers = {
                    "Host": "capi.tianyancha.com",
                    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                 "\"Google "
                                 "Chrome\";v=\"114\"",
                    "sec-ch-ua-platform": "\"Windows\"",
                    "X-TYCID": self.Request["cookie_dict"]["TYCID"],
                    "DNT": "1",
                    "sec-ch-ua-mobile": "?0",
                    "User-Agent": self.Request['ua'],
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/plain, */*",
                    "X-AUTH-TOKEN": self.Request["token"],
                    "version": "TYC-Web",
                    "Origin": "https://www.tianyancha.com",
                    "Sec-Fetch-Site": "same-site",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Referer": "https://www.tianyancha.com/",
                    "Accept-Language": "zh-CN,zh;q=0.9"}
                with ThreadPoolExecutor(3) as f:
                    all_list = []
                    _ = 1
                    while True:
                        res=self.local_conn.lpop(self.area_key)
                        if res is None:
                            time.sleep(0.5)
                        else:
                            self.local_conn.lpush(self.area_key+"_1", res)
                            self.local_conn.lpush(self.area_key+"_2", res)
                            self.local_conn.lpush(self.area_key+"_3", res)
                            self.local_conn.lpush(self.area_key+"_4", res)
                            info = json.loads(res.decode("utf-8"))
                            if "_id" in info:
                                del info['_id']
                            print(info)
                            if not self.local_conn.sismember(self.sbxx_filter_key,info["company"]):
                                all_list.append(f.submit(self.sbxx,info=info,page=1))
                            else:
                                logger.warning(f"存在 商标 信息:{info}")
                            # 作品著作权
                            # info ={"company": "青岛啤酒股份有限公司", "id": 4651392}
                            # page=1
                            # self.zpzzq(info)
                            if not self.local_conn.sismember(self.zpzzq_filter_key, info["company"]):
                                all_list.append(f.submit(self.zpzzq, info=info,page=1))
                            else:
                                logger.warning(f"存在 作品著作权 信息:{info}")
                            # 软件
                            # info = {"company": "浪潮集团有限公司", "id": 6923813}
                            # page=1
                            # self.rzzzq(info)
                            if not self.local_conn.sismember(self.rzzzq_filter_key, info["company"]):
                                all_list.append(f.submit(self.rzzzq, info=info,page=1))
                            else:
                                logger.warning(f"存在 软件著作权 信息:{info}")
                            #资质
                            # info = {"company": "中建八局第一建设有限公司", "id":271787999}
                            # page = 1
                            # self.zzzs(info)
                            if not self.local_conn.sismember(self.zzzs_filter_key, info["company"]):
                                all_list.append(f.submit(self.zzzs, info=info,page=1))
                            else:
                                logger.warning(f"存在 资质证书 信息:{info}")
                            # 行政许可
                            # info = {"company": "山东蓝海股份有限公司", "id": 32970803}
                            # page=1
                            # self.xzxk(info)
                            if not self.local_conn.sismember(self.xzxk_filter_key, info["company"]):
                                all_list.append(f.submit(self.xzxk, info=info,page=1))
                            else:
                                logger.warning(f"存在 行政许可 信息:{info}")
                            #电信许可
                            # info = {"company": "阿里云计算有限公司", "id": 138473506}
                            # page = 1
                            # self.dxxk(info)
                            if not self.local_conn.sismember(self.dxxk_filter_key, info["company"]):
                                all_list.append(f.submit(self.dxxk, info=info,page=1))
                            else:
                                logger.warning(f"存在 电信许可 信息:{info}")
                            logger.info(f"。。。。。。。。。。。。。。第 {_} 家公司！！")
                            _+=1
                            if len(all_list) >= 30:
                                for future in all_list:
                                    try:
                                        future.result()
                                    except Exception as e:
                                        logger.error(e)
                                all_list.clear()
                    for future in all_list:
                        try:
                            future.result()
                        except Exception as e:
                            logger.error(e)
                    break


if __name__ == '__main__':
    NoMemerySpider("chongqing").main()
