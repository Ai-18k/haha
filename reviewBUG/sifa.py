# _*_ coding:UTF-8 _*
import json
import math
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import redis
from loguru import logger
from pymongo import MongoClient
from retrying import retry
# from PikaUse import mongoToMQ
import requests
import datetime as ts

def compare_to_current_time(timestamp):
    # 将日期字符串转换为 datetime 对象
    given_date = datetime.strptime(timestamp,"%Y-%m-%d").date()
    # 获取当前日期
    current_date = datetime.now().date()
    # 比较给定日期与当前日期
    if given_date < current_date:
        return 1  # "历史日期"
    elif given_date > current_date:
        return 0  # "未来日期"
    elif given_date > current_date:
        return 3   #"当前日期"
    else:
        return 403  #格式不正确

class FLSS:

    def __init__(self):
        self.conn = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123",socket_connect_timeout=170)
        self.local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=170)
        self.Request=None
        self.headers = None
        self.session=requests.session()
        self.ua=None
        self.client_01 = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",authSource="admin")
        self.client=MongoClient(host='192.168.5.167', port=27017)
        self.cli_5 = self.client["shanghai"]["company_id"]
        self.cli = self.client["shanghai"]["sfaj"]
        self.cli_1 = self.client["shanghai"]["zlxx"]
        self.coll_2 = self.client_01["shanghai"]["司法案件"]
        self.coll_2_1 = self.client_01["shanghai"]["fail_司法案件"]
        self.coll_3 = self.client_01["shanghai"]["专利"]
        self.coll_3_1 = self.client_01["shanghai"]["fail_专利"]
        self.coll_4 = self.client_01["shanghai"]["fail_company_id"]
        self.sfaj_item = list()
        self.zlxx_item = list()
        self.page = 1
        self.page1 = 1
        self.page_num5=1
        self.page_num4=1
        self.page_num2=2

    @staticmethod
    def compare_to_current_time(timestamp):
        # 将日期字符串转换为 datetime 对象
        given_date = datetime.strptime(timestamp, "%Y-%m-%d").date()
        # 获取当前日期
        current_date = datetime.now().date()
        # 比较给定日期与当前日期
        if given_date < current_date:
            return 1  # "历史日期"
        elif given_date > current_date:
            return 0  # "未来日期"
        elif given_date > current_date:
            return 3  # "当前日期"
        else:
            return 403  # 格式不正确


    # 司法案件   已测试
    @retry(wait_fixed=1000)
    def sfaj(self,info):
        url = "https://capi.tianyancha.com/cloud-judicial-risk/judicialCase/list/v2"
        while True:
            params = {
                "_": str(int(time.time() * 1000))}
            data = {
                # "gid": 2343820668,
                "gid": info["id"],
                "pageSize": 10,
                "pageNum": self.page1,
                "caseIdentity": "-100",
                "caseReason": "-100",
                "caseType": "-100",
                "trialProcedure": "-100",
                "caseTag": "-100",
                "year": "-100",
                "caseLocation": "-100",
                "fullSearchText": "",
                "needFilter": 1,
                "isSameSerialCaseAgg": 1,
                "caseTitle": "",
                "source": ""}
            # data = {
            #     "gid": "2343820668",
            #     "pageSize": 10,
            #     "pageNum": self.page1,
            #     "caseIdentity": "-100",
            #     "caseReason": "-100",
            #     "caseType": "-100",
            #     "trialProcedure": "-100",
            #     "caseTag": "-100",
            #     "year": "-100",
            #     "caseLocation": "-100",
            #     "fullSearchText": "",
            #     "needFilter": 1.txt,
            #     "isSameSerialCaseAgg": 1.txt,
            #     "caseTitleId": "",
            #     "source": ""
            # }
            data = json.dumps(data, separators=(',', ':'))
            response = self.session.post(url, headers=self.headers, params=params, data=data)
            logger.info('【***正在采集司法案件***】')
            print(response.text)
            if response.status_code == 200:
                if response.json()["errorCode"]==0:
                    if response.json().get("data")["items"]:
                        num = math.ceil(int(response.json()['data']['count']) / 10) if response.json()['data'][
                            'count'] else 0
                        logger.info(f'这个链接共{num}页数据')
                        logger.info(f'当前是第{self.page1}页')
                        if self.page1 > num:
                            break  # time.sleep(0.5)
                        info_list = response.json().get("data")["items"]
                        for item in info_list:
                            # self.coll_2.insert_one(item)
                            # 关联公司名称
                            relation_company_name = info["company"]
                            # 案件名称
                            judicial_name = item["caseTitle"] if item[
                                "caseTitle"] else None
                            # 相关案号
                            judicial_number = ",".join(
                                i for i in item["caseCodeList"]) if item[
                                "caseCodeList"] else None
                            # 判断是否为历史
                            history = compare_to_current_time(item["trialTime"]) if item[
                                "trialTime"] else None
                            # 单位
                            judicial_unit = ",".join(
                                i for i in item["courtList"]) if item[
                                "courtList"] else None
                            record_date = datetime.strptime(item["trialTime"], "%Y-%m-%d").date().strftime(
                                "%Y-%m-%d") if \
                                item["trialTime"] else None
                            # 案件类型
                            info_type = item["caseType"] if item["caseType"] else None
                            # 案件身份
                            ajsf = item["caseIdentityList"][0]["caseIdentity"] if len(
                                item["caseIdentityList"]) != 0 else None if item["caseIdentityList"] else None

                            sf_dqslcx = item["trialProcedure"] if item[
                                "trialProcedure"] else None
                            # 案由
                            ay = item["caseReason"] if item[
                                "caseReason"] else None
                            info_item = {
                                "relationCompanyName": relation_company_name,
                                "judicialType": info_type,"sifaanjian "
                                "judicialName": judicial_name,
                                "judicialNumber": judicial_number,
                                "history": history,
                                "judicialUnit": judicial_unit,
                                "recordDate": record_date,
                                "filingDate": None,
                                "judicialMoney": None,
                                "infoType": None,
                                "judicialContent": None,
                                "sjmc": None,
                                "ajsf": ajsf,
                                'otherIdentity': "[]",
                                "ay": ay,
                                "sfDqslcx": sf_dqslcx,
                                "xfXfdx": None,
                                "xfGldx": None,
                                "xfSql": None,
                                "bzxr": None,
                                "sxSxxw": None,
                                "sxLxqk": None,
                                "jyYcrq": None,
                                "jyYcyy": None,
                                "gqStatus": None
                            }
                            # self.cli.insert_one(info_item)
                            if "_id" in info_item:
                                del info_item["_id"]
                            logger.success(f"司法数据保存成功:{info_item}!!")
                            logger.info(f"第 {self.page1} 页数据！！")
                            self.send_data(3,info_item)
                    else:
                        break
                elif response.json()["errorCode"]==302004:
                    res = self.conn.rpop("searchCookie")
                    if res is None:
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
                            "X-TYCID": self.Request['sign'],
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
                        logger.warning("正在重新登录！！")
                        raise Exception("失效")
                else:
                    res = self.conn.lpop("searchCookie")
                    if res is None:
                        time.sleep(1)
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
                            "X-TYCID": self.Request['sign'],
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
                        raise Exception("失效")
            self.local_conn.sadd("shanghai:filter:sfaj",info["company"])
            self.page1+=1
            break


    # 专利信息    已测试
    def zlxx(self, info):
        # try:
        while True:
            url = "https://capi.tianyancha.com/cloud-intellectual-property/patent" \
                  "/patentListV6"
            params = {
                "_": str(int(time.time() * 1000)),
                "id": info["id"],
                # "id": 2343820668,
                "pageSize": "10",
                "pageNum": self.page,
                "type": "-100",
                "lprs": "-100",
                "applyYear": "-100",
                "pubYear": "-100",
                "fullSearchText": "",
                "sortField": "",
                "sortType": "-100"}
            response = self.session.get(url, headers=self.headers, params=params)
            logger.info('【***正在采集专利信息***】')
            print(response.json())
            if response.status_code == 200:
                if response.json()["errorCode"] == 0:
                    num = math.ceil(int(response.json()['data']['viewtotal']) / 10) if response.json()['data'][
                        'viewtotal'] else 0
                    if self.page > num:
                        break
                    logger.info(f'这个链接共{num}页数据')
                    logger.info(f'当前是第{self.page}页')
                    info_list = response.json().get("data")["items"]
                    for patent_data in info_list:
                        print(patent_data)
                        # self.coll_3.insert_one(patent_data)
                        property_title = patent_data["title"] if patent_data["title"] else None
                        # 申请号
                        property_num = patent_data["appnumber"] if patent_data["appnumber"] else None
                        # 申请日
                        try:
                            filing_date = datetime.strptime(patent_data["applicationTime"], "%Y-%m-%d").date() if \
                                patent_data["applicationTime"] else None
                        except:
                            filing_date = None
                        # 公开日
                        try:
                            gain_date = datetime.strptime(patent_data["pubDate"], "%Y-%m-%d") if patent_data[
                                "pubDate"] else None
                        except:
                            gain_date =None
                        # 专利类型
                        info_type = patent_data["patentType"] if patent_data["patentType"] else None
                        # 专利状态
                        info_status = patent_data["lprs"] if patent_data["lprs"] else None
                        create_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # 关联公司
                        relation_company_name = patent_data["applicantName"] if patent_data[
                            "applicantName"] else None
                        if "inventor" in patent_data:
                            zl_inventor = patent_data["inventor"] if patent_data["inventor"] else None
                        else:
                            zl_inventor =None
                        if "pubnumber" in patent_data:
                            zl_open_num = patent_data["pubnumber"] if patent_data["pubnumber"] else None
                        else:
                            zl_open_num =None
                        logger.info((0, "专利", property_title, property_num, filing_date, gain_date,
                                     info_type, info_status, None, 1, None, None, None, 0, None,
                                     relation_company_name,
                                     None, zl_inventor, zl_open_num, None, None, None))
                        info_item = {
                            "propertyType": "专利",
                            "propertyTitle": property_title,
                            "propertyNum": property_num,
                            "filingDate": patent_data["applicationTime"] if patent_data[
                                "applicationTime"] else None,
                            "gainDate": gain_date,
                            "infoType": info_type,
                            "infoStatus": info_status,
                            "content": None,
                            "relationCompanyName": relation_company_name,
                            "sbImageUrl": None,
                            "zlInventor": zl_inventor,
                            "zlOpenNum": zl_open_num,
                            "rzSimpleName": None,
                            "rzVersionsNum": None,
                            "zpCompletionDate": None
                        }
                        # self.cli_1.insert_one(info_item)
                        logger.info(info_item)
                        if "_id" in info_item:
                            del info_item["_id"]
                        logger.info(f"第 {self.page} 页数据！！")
                        self.send_data(4, info_item)
                        logger.success(f"专利数据保存成功:{info_item}!!")
                else:
                    self.page += 1
                    while True:
                        res = self.conn.lpop("searchCookie")
                        if res is None:
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
                                "X-TYCID": self.Request['sign'],
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
                            raise Exception("失效")
            self.local_conn.sadd("shanghai:filter:zlxx_com", info["company"])
            self.page += 1
    # except Exception as e:
    #     logger.error(e)

    #历史行政处罚
    # @retry(wait_fixed=1000)
    def adminpen(self, info):
        # try:
        while True:
            url = "https://capi.tianyancha.com/cloud-operating-risk/operating/punishment/punishIndexList"
            params = {
                "withOwner": "0",
                "_": str(int(time.time() * 1000)),
                "pageSize": "10",
                "pageNum": self.page_num5,
                "gid": info["id"]
            }
            response = requests.get(url, headers=self.headers, params=params)
            print("【*】行政处罚--->", response.json())
            if response.status_code == 200:
                if response.json()['state'] == "ok":
                    if response.json()['message'] == "":
                        num = math.ceil(int(response.json()["data"]["totalCount"]) / 10) if \
                            response.json()["data"][
                                "totalCount"] else 0
                        logger.info(f'这个链接共{num}页数据')
                        logger.info(f'当前是第{self.page_num5}页')
                        if self.page_num5 > num:
                            break
                        info_list = response.json()["data"]["list"]
                        for item in info_list:
                            item["companyName"] = info["company"]
                            # self.coll_8.insert_one(item)
                            # 相关案号
                            judicial_number = item["punishNumber"] if item["punishNumber"] else None
                            # 执行法院
                            judicial_unit = item["punishDepartment"] if item["punishDepartment"] else None
                            # 发布日期
                            try:
                                record_date = datetime.strptime(item["admin_punish_date"],
                                                                "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d") \
                                    if item["admin_punish_date"] != "0000-00-00 00:00:00" else None if item[
                                    "admin_punish_date"] else None
                            except:
                                record_date =None
                            # 判断是否为历史
                            # history = self.compare_to_current_time(record_date) if record_date else None
                            info_type = item["punishReason"]
                            judicial_content = item["punishContent"]
                            json_data = {
                                'relationCompanyName': info["company"],
                                'judicialType': '行政处罚',
                                'history': 0,
                                'judicialUnit': judicial_unit,
                                'recordDate': record_date,
                                'judicialName': '',
                                'judicialNumber': judicial_number,
                                'filingDate': "",
                                'judicialMoney': "",
                                'infoType': info_type,
                                'judicialContent': judicial_content,
                                'sjmc': '',
                                'ajsf': "",
                                'otherIdentity': "[]",
                                'ay': "",
                                'sfDqslcx': '',
                                'xfXfdx': '',
                                'xfGldx': '',
                                'xfSql': '',
                                'bzxr': "",
                                'sxSxxw': "",
                                'sxLxqk': "",
                                'jyYcrq': '',
                                'jy_ycyy': '',
                                'gqStatus': '',
                            }
                            # self.coll_8_1.insert_one(json_data)
                            if "_id" in json_data:
                                del json_data["_id"]
                            logger.success(f"司法数据保存成功:{json_data}!!")
                            logger.info(f"第 {self.page_num5} 页数据！！")
                            # self.send_data(3, json_data)
                            # break
                    else:
                        while True:
                            res = self.conn.lpop("searchCookie")
                            if res is None:
                                print(">>>>>>>>>>>>获取cookie信息.................")
                                time.sleep(0.5)
                            else:
                                self.Request = json.loads(res.decode("utf-8"))
                                print(self.Request)
                                self.session.cookies = requests.utils.cookiejar_from_dict(
                                    self.Request["cookie_dict"])
                                self.headers = {
                                    "Host": "capi.tianyancha.com",
                                    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                                 "\"Google "
                                                 "Chrome\";v=\"114\"",
                                    "sec-ch-ua-platform": "\"Windows\"",
                                    "X-TYCID": self.Request['sign'],
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
                                raise Exception("失效")
                else:
                    while True:
                        res = self.conn.lpop("searchCookie")
                        if res is None:
                            print(">>>>>>>>>>>>获取cookie信息.................")
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
                                "X-TYCID": self.Request['sign'],
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
                            raise Exception("失效")
            self.page_num5 += 1
            # break

    # 失信被执行人
    def jdefaulters(self, info):
        # try:
        while True:
            url = "https://capi.tianyancha.com/cloud-judicial-risk/risk/dishonest"
            params = {
                "_": str(int(time.time() * 1000)),
                "keyWords": info["company"],
                "pageSize": "10",
                "pageNum": self.page_num4,
                "gid": info["id"],
                "performance": "-100",
                "year": "-100",
                "fullSearchText": ""
            }
            response = requests.get(url, headers=self.headers, params=params)
            print("【*】 失信被执行人-->", response.json())
            if response.status_code == 200:
                if response.json()["state"] == "ok":
                    if response.json()["data"]:
                        if response.json()['message'] != "登录后可查看更多":
                            num = math.ceil(int(json.loads(response.json()["data"])['total']) / 10) if \
                            json.loads(response.json()["data"])['total'] else 0
                            logger.info(f'这个链接共{num}页数据')
                            logger.info(f'当前是第{self.page_num4}页')
                            if self.page_num4 > num:
                                break
                            info_list = json.loads(response.json()["data"])["items"]
                            for item in info_list:
                                item["companyName"] = info["company"]
                                # self.coll_7.insert_one(item)
                                # 相关案号
                                judicial_number = item["casecode"] if item["casecode"] else None
                                # 执行法院
                                judicial_unit = item["gistunit"] if item["gistunit"] else None
                                # 发布日期
                                try:
                                    record_date = ts.datetime.fromtimestamp(
                                        item["publishdate"] / 1000).strftime('%Y-%m-%d') if item[
                                        "publishdate"] else None
                                except:
                                    record_date =None
                                # 立案日期
                                try:
                                    filing_date = ts.datetime.fromtimestamp(
                                        item["regdate"] / 1000).strftime('%Y-%m-%d') if item["regdate"] else None
                                except:
                                    filing_date =None
                                # 判断是否为历史
                                # history = self.compare_to_current_time(record_date) if record_date else None
                                bzxr = item["iname"] if item["iname"] else None
                                sx_sxxw = item["disrupttypename"] if item["disrupttypename"] else None
                                sx_lxqk = item["performance"] if item["performance"] else None
                                json_data = {
                                    'relationCompanyName': info["company"],
                                    'judicialType': '失信被执行人',
                                    'history': 0,
                                    'judicialUnit': judicial_unit,
                                    'recordDate': record_date,
                                    'judicialName': '',
                                    'judicialNumber': judicial_number,
                                    'filingDate': filing_date,
                                    'judicialMoney': "",
                                    'infoType': "",
                                    'judicialContent': "",
                                    'sjmc': '',
                                    'ajsf': "",
                                    'otherIdentity': "[]",
                                    'ay': "",
                                    'sfDqslcx': '',
                                    'xfXfdx': '',
                                    'xfGldx': '',
                                    'xfSql': '',
                                    'bzxr': bzxr,
                                    'sxSxxw': sx_sxxw,
                                    'sxLxqk': sx_lxqk,
                                    'jyYcrq': '',
                                    'jy_ycyy': '',
                                    'gqStatus': '',
                                }
                                # self.coll_7_1.insert_one(json_data)
                                if "_id" in json_data:
                                    del json_data["_id"]
                                logger.success(f"司法数据保存成功:{json_data}!!")
                                logger.info(f"第 {self.page_num4} 页数据！！")
                                # self.send_data(3, json_data)
                                # break
                        else:
                            while True:
                                res = self.conn.lpop("searchCookie")
                                if res is None:
                                    print(">>>>>>>>>>>正在获取cookie信息.............")
                                    time.sleep(0.5)
                                else:
                                    self.Request = json.loads(res.decode("utf-8"))
                                    print(self.Request)
                                    self.session.cookies = requests.utils.cookiejar_from_dict(
                                        self.Request["cookie_dict"])
                                    self.headers = {
                                        "Host": "capi.tianyancha.com",
                                        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                                     "\"Google "
                                                     "Chrome\";v=\"114\"",
                                        "sec-ch-ua-platform": "\"Windows\"",
                                        "X-TYCID": self.Request['sign'],
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
                                    raise Exception("失效")
                    else:
                        break
                elif response.json()["state"] == "warn":
                    break
                else:
                    while True:
                        res = self.conn.lpop("searchCookie")
                        if res is None:
                            print(">>>>>>>>>>>正在获取cookie信息.............")
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.session.cookies = requests.utils.cookiejar_from_dict(
                                self.Request["cookie_dict"])
                            self.headers = {
                                "Host": "capi.tianyancha.com",
                                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                             "\"Google "
                                             "Chrome\";v=\"114\"",
                                "sec-ch-ua-platform": "\"Windows\"",
                                "X-TYCID": self.Request['sign'],
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
                            raise Exception("失效")
            self.page_num4 += 1
            # break
    # except:
    #     self.col.insert_one(info)

    # 历史裁判文书
    def Nohishear(self, info):
        # try:
            while True:
                url = "https://capi.tianyancha.com/cloud-history-information/historyJudicialRisk/lawsuitWithLabel"
                params = {
                    "_": str(int(time.time() * 1000)),
                    "pageSize": "10",
                    "pageNum": self.page_num2,
                    "keyWords": "",
                    "id": info["id"],
                    # "id": 22822,
                    "identity": "-100",
                    "casereason": "-100",
                    "publishYear": "-100",
                    "area": "-100",
                    "courtLevel": "-100",
                    "judgeResult": "-100",
                    "caseType": "-100",
                    "documentType": "-100",
                    "procType": "-100",
                    "caseAmt": "-100",
                    "fullSearchText": ""
                }
                response = self.session.get(url, headers=self.headers, params=params)
                print("【*】历史裁判文书-->", response.json())
                if response.status_code == 200:
                    if response.json()["errorCode"] == 0:
                        if response.json()['message'] != "登录后可查看更多":
                            num = math.ceil(int(response.json()["data"]['total']) / 10) if response.json()["data"][
                                'total'] else 0
                            logger.info(f'这个链接共{num}页数据')
                            logger.info(f'当前是第{self.page_num2}页')
                            if self.page_num2 > num:
                                break
                            info_list = response.json()["data"]["items"]
                            for item in info_list:
                                item["companyName"] = info["company"]
                                # self.coll_5.insert_one(item)
                                list2 = set()
                                if "plaintiffList" in item:
                                    data = item["plaintiffList"]
                                    for aa in data:
                                        if aa["role"] in info:
                                            info[aa["role"]] = info[aa["role"]] + [aa["name"]]
                                        else:
                                            info[aa["role"]] = [aa["name"]]
                                        list2.add(aa["role"])
                                if "defendantList" in item:
                                    data1 = item["defendantList"]
                                    for bb in data1:
                                        if bb["role"] in info:
                                            info[bb["role"]] = info[bb["role"]] + [bb["name"]]
                                        else:
                                            info[bb["role"]] = [bb["name"]]
                                        list2.add(bb["role"])
                                otherIdentity = list()
                                ajsf = ""
                                for i in list2:
                                    zz = dict()
                                    zz["identity"] = i
                                    zz["list"] = list(set(info[i]))
                                    if info["company"] in info[i]:
                                        ajsf = i
                                    otherIdentity.append(zz)
                                # 案件名称
                                judicial_name = item["title"]
                                # 相关案号
                                judicial_number = item["caseno"] if item[
                                    "caseno"] else None
                                # 执行法院
                                judicial_unit = item["court"] if item["court"] else None
                                # 发布日期
                                try:
                                    record_date = ts.datetime.fromtimestamp(int(item["submittime"])).strftime(
                                        '%Y-%m-%d')
                                except:
                                    record_date = None
                                try:
                                    filing_date = ts.datetime.fromtimestamp(int(
                                        item["judgetime"]) / 1000).strftime(
                                        '%Y-%m-%d')
                                except:
                                    filing_date = None
                                # 判断是否为历史
                                # history = self.compare_to_current_time(filing_date) if \
                                #     filing_date else None
                                # 裁判结果
                                if "judgment" in item:
                                    judicial_content = item["judgment"]
                                    judicial_content = re.sub("<(.*?)>", "", judicial_content)
                                else:
                                    judicial_content = None
                                ay = item["casereason"] if item["casereason"] else None
                                json_data = {
                                    'relationCompanyName': info["company"],
                                    'judicialType': "裁判文书",
                                    'history': 1,
                                    'judicialUnit': judicial_unit,
                                    'recordDate': record_date,
                                    'judicialName': judicial_name,
                                    'judicialNumber': judicial_number,
                                    'filingDate': filing_date,
                                    'judicialMoney': '',
                                    'infoType': "",
                                    'judicialContent': judicial_content,
                                    'sjmc': '',
                                    'ajsf': ajsf,
                                    'otherIdentity': otherIdentity,
                                    'ay': ay,
                                    'sfDqslcx': '',
                                    'xfXfdx': '',
                                    'xfGldx': '',
                                    'xfSql': '',
                                    'bzxr': '',
                                    'sxSxxw': '',
                                    'sxLxqk': '',
                                    'jyYcrq': '',
                                    'jy_ycyy': '',
                                    'gqStatus': '',
                                }
                                # self.coll_5_1.insert_one(json_data)
                                if "_id" in json_data:
                                    del json_data["_id"]
                                logger.success(f"司法数据保存成功:{json_data}!!")
                                logger.info(f"第 {self.page_num2} 页数据！！")
                                # self.send_data(3, json_data)
                                # break
                        else:
                            while True:
                                res = self.conn.lpop("searchCookie")
                                if res is None:
                                    print(">>>>>>>>>>>>获取cookie信息.................")
                                    time.sleep(0.5)
                                else:
                                    self.Request = json.loads(res.decode("utf-8"))
                                    print(self.Request)
                                    self.session.cookies = requests.utils.cookiejar_from_dict(
                                        self.Request["cookie_dict"])
                                    self.headers = {
                                        "Host": "capi.tianyancha.com",
                                        "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", "
                                                     "\"Google "
                                                     "Chrome\";v=\"114\"",
                                        "sec-ch-ua-platform": "\"Windows\"",
                                        "X-TYCID": self.Request['sign'],
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
                                    raise Exception("失效")
                    else:
                        while True:
                            res = self.conn.lpop("searchCookie")
                            if res is None:
                                print(">>>>>>>>>>>>获取cookie信息.................")
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
                                    "X-TYCID": self.Request['sign'],
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
                                raise Exception("失效")
                self.page_num2 += 1
            # break
        # except:
        #     self.col.insert_one(info)

    def Restrain(self, info):
        while True:
                url = "https://capi.tianyancha.com/cloud-judicial-risk/risk/getRestrictOrder"
                params = {
                    "_": str(int(time.time() * 1000)),
                    "gid": info["id"],
                    "pageSize": "10",
                    "pageNum": self.page
                }
                response = self.session.get(url, headers=self.headers, params=params)
                print("【*】限制消费---->", response.json())
                if response.status_code == 200:
                    if response.json()["errorCode"] == 0:
                        if response.json()["data"]:
                            if response.json()['message'] == "":
                                num = math.ceil(int(response.json()["data"]['count']) / 10) if \
                                response.json()["data"][
                                    'count'] else 0
                                logger.info(f'这个链接共{num}页数据')
                                logger.info(f'当前是第{self.page}页')
                                if self.page > num:
                                    break
                                info_list = response.json()["data"]["items"]
                                for item in info_list:
                                    item["companyName"] = info["company"]
                                    self.coll_4.insert_one(item)
                                    # 相关案号
                                    judicial_number = item["caseCode"] if item["caseCode"] else None
                                    # 判断是否为历史
                                    history = self.compare_to_current_time(item["publishDate"]) if item[
                                        "publishDate"] else None
                                    # 执行法院
                                    judicial_unit = item["execCourtName"] if item["execCourtName"] else None
                                    # 发布日期
                                    try:
                                        record_date = item["publishDate"] if item["publishDate"] else None
                                    except:
                                        record_date = None
                                    # 立案日期

                                    if item["caseCreateTime"]:
                                        try:
                                            filing_date = ts.datetime.fromtimestamp(item["caseCreateTime"] / 1000).strftime('%Y-%m-%d') if not isinstance(item["caseCreateTime"], str) else item["caseCreateTime"]
                                        except:
                                            filing_date = None
                                    else:
                                        None
                                    xf_xfdx = item["qyinfo"] if item["qyinfo"] else None
                                    xf_gldx = item["xname"] if item["xname"] else None
                                    xf_sql = item["applicant"] if item["applicant"] else None
                                    json_data = {
                                        'relationCompanyName': info["company"],
                                        'judicialType': '限制消费',
                                        'history': 0,
                                        'judicialUnit': judicial_unit,
                                        'recordDate': record_date,
                                        'judicialName': '',
                                        'judicialNumber': judicial_number,
                                        'filingDate': filing_date,
                                        'judicialMoney': "",
                                        'infoType': "",
                                        'judicialContent': "",
                                        'sjmc': '',
                                        'ajsf': "",
                                        'otherIdentity': "[]",
                                        'ay': "",
                                        'sfDqslcx': '',
                                        'xfXfdx': xf_xfdx,
                                        'xfGldx': xf_gldx,
                                        'xfSql': xf_sql,
                                        'bzxr': "",
                                        'sxSxxw': "",
                                        'sxLxqk': "",
                                        'jyYcrq': "",
                                        'jy_ycyy': "",
                                        'gqStatus': '',
                                    }
                                    logger.info(json_data)
                                    self.coll_4_1.insert_one(json_data)
                                    if "_id" in json_data:
                                        del json_data["_id"]
                                    logger.success(f"司法数据保存成功:{json_data}!!")
                                    logger.info(f"第 {self.page} 页数据！！")
                                    self.send_data(3, json_data)
                                    # break
                self.page+=1


    def run(self):
            res = self.local_conn.lpop("searchCookie")
            if res is None:
                time.sleep(1)
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
                    "X-TYCID": self.Request['sign'],
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
                # currentPage = int(self.local_conn.get("shanghai:ON_num"))
                # pageSize = 1000
                # with ThreadPoolExecutor(3) as f:
                #     all_list=[]
                #     while True:
                #         data=self.cli_5.find({}, {"_id": False}).skip((currentPage - 1.txt) * pageSize).limit(pageSize)
                #         _ = 1.txt
                #         for company_id in data[_:]:
                #             print(company_id)
                #             if "_id" in company_id:
                #                 del company_id["_id"]
                """"""
                # company_id={"company":"费县甜蜜蜜农业种植专业合作社","id":7021957930}
                # if not self.local_conn.sismember("shanghai:filter:sfaj",company_id["company"]):
                #         # res=f.submit(self.sfaj,info=company_id)
                #         # all_list.append(res)
                #         self.page1=1.txt
                #         self.sfaj(company_id)
                # else:
                #     logger.warning(f"【*】司法已过滤:{company_id}")
                """测试专利数据"""
                # company_id = {"company": "先尼科化工（上海）有限公司", "id": 346063766}
                # self.page=5
                # self.zlxx(company_id)
                """"""
                """{'state': 'ok', 'message': '', 'special': '', 'vipMessage': '', 'isLogin': 0, 'errorCode': 0, 'data': {'companyGraphId': 4733837777, 'count': 1.txt, 'year_lmbx': [{'value': '-100', 'key': '全部年份', 'itemKey': '全部年份'}, {'value': '2024', 'key': '2024（1.txt）', 'itemKey': '2024', 'itemCount': 1.txt}], 'historyCount': 2, 'items': [{'caseCode': '(2024)陕0112执恢4303号', 'serviceType': 1.txt, 'gid': 1855185201, 'applicantList': [{'applicantCid': '4235736541', 'applicantAlias': '劳利斯', 'applicantLogo': None, 'applicantType': 1.txt, 'applicant': '陕西劳利斯建筑工程有限公司'}], 'zhixingId': None, 'filePath': 'http://zxgk.court.gov.cn/xglfile/3606/2024-09-04/29688b4dcba94d77a36343d8a1f5949d.pdf', 'publishDate': '2024-09-04 00:00:00', 'businessId': 'e9v9mov7f0b343220b014010flb3m2b8', 'execCourtName': '西安市未央区人民法院', 'type': 2, 'xname': '周明义', 'caseUuid': '20bfaea2d6c84033ab65f8f718827550', 'applicant': '陕西劳利斯建筑工程有限公司', 'toco': 6, 'serviceCount': 6, 'hasOssPath': 0, 'qyinfo': '', 'caseCreateTime': 1724774400000, 'logo': None, 'alias': None, 'explainMessage': None, 'id': '67278423', 'ossPath': '', 'cid': 4733837777}]}}"""
                company_id={"company": "陕西劳利斯建筑工程有限公司", "id": 1855185201}
                self.Restrain(company_id)

                # company_id = {"company": "广州禧臻运输有限公司", "id": 2341514248}
                # company_id = {"company": "济南宏仁大药店有限公司", "id": 2337611216}
                # company_id = {"company": "广州市越秀区鼎友宾馆（普通合伙）", "id": 3004647946}
                # self.adminpen(company_id)

                # company_id = {"company": "山东天芯元电子科技有限公司", "id": 3295696772}
                # company_id = {"company": "山东齐翔航空科技有限公司", "id": 3018977725}
                # self.jdefaulters(company_id)

                # company_id = {"company": "广州格凌康药业有限公司", "id":1572233979}
                # self.Nohishear(company_id)



if __name__ == '__main__':
    FLSS().run()





