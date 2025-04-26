# _*_ coding:UTF-8 _*
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor
import datetime
import redis
from loguru import logger
from pymongo import MongoClient
from MQitems.PikaUse import mongoToMQ
# from Login.simpleLogin import Login_module
import requests


class NoMemerySpider:

    def __init__(self):
        self.session = requests.session()
        self.conn = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123", socket_connect_timeout=170)
        self.local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",
                                      socket_connect_timeout=170)
        self.client_01 = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",
                                     authSource="admin")
        self.client = MongoClient(host='192.168.5.167', port=27017)

        self.cli_5 = self.client["shanghai"]["company_id"]

        self.coll = self.client_01['shanghai']['商标信息']
        self.coll1 = self.client_01['shanghai']['作品著作权']
        self.coll2 = self.client_01['shanghai']['电信许可']
        self.coll3 = self.client_01['shanghai']['软著著作权']
        self.coll4 = self.client_01['shanghai']['行政许可']
        self.coll5 = self.client_01['shanghai']['资质证书']

        self.cli=self.client['shanghai']['商标信息']
        self.cli1=self.client['shanghai']['作品著作权']
        self.cli2=self.client['shanghai']['电信许可']
        self.cli3=self.client['shanghai']['软著著作权']
        self.cli4=self.client['shanghai']['行政许可']
        self.cli5=self.client['shanghai']['资质证书']

        self.c_fail = self.client['shanghai']['fail_商标信息']
        self.c_fail1 = self.client['shanghai']['fail_作品著作权']
        self.c_fail2 = self.client['shanghai']['fail_电信许可']
        self.c_fail3 = self.client['shanghai']['fail_软著著作权']
        self.c_fail4 = self.client['shanghai']['fail_行政许可']
        self.c_fail5 = self.client['shanghai']['fail_资质证书']

        self.sbxx_list=list()   #4
        self.zpzzq_list=list()  #5
        self.rzzzq_list=list()  #6
        self.f_map = {"4": self.sbxx_list, "5": self.zpzzq_list,"6": self.rzzzq_list}
        self.Request=dict()
        self.headers=dict()


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
                response = requests.post(url, headers=self.headers, params=params, data=data)
                data=response.json()
                print(data)
                if data["state"] == "ok":
                    num = math.ceil(int(data['data']['viewtotal']) / 10) if data['data']['viewtotal'] else 0
                    logger.info(f'这个链接共{num}页数据')
                    logger.info(f'当前是第{page}页')
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
                            # logger.info(f"第 {page} 页数据！！")
                            logger.success(f"【*】商标数据保存成功:{data}!!")
                else:
                    while True:
                        res = self.local_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["sign"],
                                "DNT": "1.txt",
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
                self.c_fail.insert_one(info)
            page+=1
        self.local_conn.sadd("shanghai:filter:sbxx", info["company"])

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
                response = requests.get(url,headers=self.headers,params=params)
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
                else:
                    while True:
                        res = self.local_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["sign"],
                                "DNT": "1.txt",
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
                self.c_fail1.insert_one(info)
            page+=1
        self.local_conn.sadd("shanghai:filter:zpzzq", info["company"])

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
                response = requests.get(url,headers=self.headers,params=params)
                data = response.json()
                if data["state"] == "ok":
                    print(data)
                    num = math.ceil(int(data['data']['total']) / 10) if data['data']['total'] else 0
                    logger.info(f'这个链接共{num}页数据')
                    logger.info(f'当前是第{page}页')
                    if page > num :
                        break
                    data=response.json()
                    if response.status_code == 200:
                        for item in data['data']['items']:
                            item["companyName"] = info["company"]
                            self.coll3.insert_one(item)
                            # 将毫秒时间戳转换为秒时间戳
                            filingDate =datetime.datetime.fromtimestamp(item['regtime']/1000).strftime('%Y-%m-%d') if item['regtime'] else ""
                            gainDate = datetime.datetime.fromtimestamp(item['publishtime'] / 1000).strftime('%Y-%m-%d') if \
                            item['publishtime'] else ""
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
                else:
                    while True:
                        res = self.local_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["sign"],
                                "DNT": "1.txt",
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
                self.c_fail3.insert_one(info)
            page+=1
        self.local_conn.sadd("shanghai:filter:rzzzq", info["company"])

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
                response = requests.get(url, params=params,headers=self.headers)
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
                else:
                    while True:
                        res = self.local_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["sign"],
                                "DNT": "1.txt",
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
                self.c_fail5.insert_one(info)
            page+=1
        self.local_conn.sadd("shanghai:filter:zzzs", info["company"])


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
                response = requests.get(url, params=params,headers=self.headers)
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
                else:
                    while True:
                        res = self.local_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["sign"],
                                "DNT": "1.txt",
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
                page+=1
            except Exception as e:
                logger.error(e)
                info["page"] = page
                self.c_fail4.insert_one(info)
        self.local_conn.sadd("shanghai:filter:xzxk", info["company"])


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
                response = requests.get(url,params=params,headers=self.headers)
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
                else:
                    while True:
                        res = self.local_conn.lpop("NoMemeryCookie")
                        if res is None:
                            print(">>>>>>>>>>>>>>获取cookie信息..........")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request["sign"],
                                "DNT": "1.txt",
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
                self.c_fail2.insert_one(info)
            page+=1
        self.local_conn.sadd("shanghai:filter:dxxk", info["company"])


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
            res = self.local_conn.lpop("NoMemeryCookie")
            if res is None:
                print(">>>>>>>>>>>>>>获取cookie信息..........")
                time.sleep(0.5)
            else:
                self.Request = json.loads(res.decode("utf-8"))
                print(self.Request)
                self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                self.headers = {
                    "Host": "capi.tianyancha.com",
                    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                 "\"Google "
                                 "Chrome\";v=\"114\"",
                    "sec-ch-ua-platform": "\"Windows\"",
                    "X-TYCID": self.Request["sign"],
                    "DNT": "1.txt",
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
                currentPage =1
                pageSize = 1000
                with ThreadPoolExecutor(3) as f:
                    all_list = []
                    for i in range(currentPage,1190):
                        data = self.cli_5.find({}, {"_id": False}).skip((currentPage - 1) * pageSize).limit(pageSize)
                        _ = 1
                        for info in data[_:]:
                            #商标
                            # info ={"company": "山东蓝海股份有限公司", "id": 32970803}
                            # page_num=1.txt
                            # self.sbxx(info)
                            if not self.local_conn.sismember("shanghai:filter:sbxx",info["company"]):
                                all_list.append(f.submit(self.sbxx,info=info,page=1))
                            else:
                                logger.warning(f"存在 商标 信息:{info}")
                            # 作品著作权
                            # info ={"company": "青岛啤酒股份有限公司", "id": 4651392}
                            # page=1.txt
                            # self.zpzzq(info)
                            if not self.local_conn.sismember("shanghai:filter:zpzzq", info["company"]):
                                all_list.append(f.submit(self.zpzzq, info=info,page=1))
                            else:
                                logger.warning(f"存在 作品著作权 信息:{info}")
                            # 软件
                            # info = {"company": "浪潮集团有限公司", "id": 6923813}
                            # page=1.txt
                            # self.rzzzq(info)
                            if not self.local_conn.sismember("shanghai:filter:rzzzq", info["company"]):
                                all_list.append(f.submit(self.rzzzq, info=info,page=1))
                            else:
                                logger.warning(f"存在 软件著作权 信息:{info}")
                            #资质
                            # info = {"company": "中建八局第一建设有限公司", "id":271787999}
                            # page = 1.txt
                            # self.zzzs(info)
                            if not self.local_conn.sismember("shanghai:filter:zzzs", info["company"]):
                                all_list.append(f.submit(self.zzzs, info=info,page=1))
                            else:
                                logger.warning(f"存在 资质证书 信息:{info}")
                            # 行政许可
                            # info = {"company": "山东蓝海股份有限公司", "id": 32970803}
                            # page=1.txt
                            # self.xzxk(info)
                            if not self.local_conn.sismember("shanghai:filter:xzxk", info["company"]):
                                all_list.append(f.submit(self.xzxk, info=info,page=1))
                            else:
                                logger.warning(f"存在 行政许可 信息:{info}")
                            #电信许可
                            # info = {"company": "阿里云计算有限公司", "id": 138473506}
                            # page = 1.txt
                            # self.dxxk(info)
                            if not self.local_conn.sismember("shanghai:filter:dxxk", info["company"]):
                                all_list.append(f.submit(self.dxxk, info=info,page=1))
                            else:
                                logger.warning(f"存在 电信许可 信息:{info}")
                            logger.info(f"。。。。。。。。。。。。。。第 {_ + (currentPage-1)*pageSize} 家公司！！")
                            _ += 1
                            if len(all_list) >= 200:
                                try:
                                    for future in all_list:
                                        future.result()
                                    all_list.clear()
                                except Exception as e:
                                    logger.error(e)
                        currentPage += 1
                        self.local_conn.set("shanghai:zizhi_num", currentPage)
                        logger.info(f">>>>>>>>>>>>>>>>>第{currentPage}页数据")


if __name__ == '__main__':
    NoMemerySpider().main()
