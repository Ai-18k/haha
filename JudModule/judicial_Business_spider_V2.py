"""
@FileName：mainSpider.py
@Description：
@Author：18k
@Time：2024/6/1 20:52
@Department：部门
@Website：站点
@Copyright：©2019-2024 职业
:return:
"""
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import pymongo
from retrying import retry
import json
import re
import time
import redis
import requests
from loguru import logger
import datetime as ts
from PikaUse import mongoToMQ


class SuccessCODE():

    def __init__(self):
        self.session = requests.Session()
        self.local_0T_conn = redis.Redis(host='192.168.5.192', port=14117, db=0, password="fer@nhaweif576KUG",socket_connect_timeout=1170)
        self.local_VQ_conn = redis.Redis(host='192.168.5.181', port=7933, db=0, password="fer@nhaweif576KUG",socket_connect_timeout=1170)
        self.Request={}
        self.client_01 = pymongo.MongoClient(host='139.9.70.234', port=12700, username="root",
                                             password="QuyHlxXhW2PSHTwT",
                                             authSource="admin")
        self.client = pymongo.MongoClient(host='192.168.5.167', port=27017)
        self.coll_2 = self.client_01["sichuan"]["法院公告"]
        self.coll_3 = self.client_01["sichuan"]["经营异常"]
        self.coll_4 = self.client_01["sichuan"]["限制消费"]
        self.coll_5 = self.client_01["sichuan"]["裁判文书"]
        self.coll_6 = self.client_01["sichuan"]["被执行人"]
        self.coll_7 = self.client_01["sichuan"]["失信被执行人"]
        self.coll_8 = self.client_01["sichuan"]["行政处罚"]
        self.coll_9 = self.client_01["sichuan"]["股权冻结"]

        self.coll_2_1 = self.client["sichuan"]["法院公告"]
        self.coll_3_1 = self.client["sichuan"]["经营异常"]
        self.coll_4_1 = self.client["sichuan"]["限制消费"]
        self.coll_5_1 = self.client["sichuan"]["裁判文书"]
        self.coll_6_1 = self.client["sichuan"]["被执行人"]
        self.coll_7_1 = self.client["sichuan"]["失信被执行人"]
        self.coll_8_1 = self.client["sichuan"]["行政处罚"]
        self.coll_9_1 = self.client["sichuan"]["股权冻结"]

        self.col = self.client["sichuan"]["fail_sifa_companyid"]
        self.headers=dict()
        self.sfaj_item=list()


    # 裁判文书
    def Nohishear(self, info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-judicial-risk/risk/lawsuit"
                params = {
                    "_": str(int(time.time() * 1000)),
                    "pageSize": "10",
                    "pageNum": page,
                    "keyWords": "",
                    "gid": info["id"],
                    # "gid": "28531752",
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
                print("【*】裁判文书-->", response.json())
                if response.status_code == 200:
                    if response.json()["state"] == "ok" and response.json()['message'] == "":
                        num = math.ceil(int(response.json()["data"]['total']) / 10) if response.json()["data"][
                            'total'] else 0
                        logger.info(f'这个链接共{num}页数据')
                        logger.info(f'当前是第{page}页')
                        if page > num:
                            break
                        info_list = response.json()["data"]["items"]
                        for item in info_list:
                            item["companyName"] = info["company"]
                            self.coll_5.insert_one(item)
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
                                zz["list"] = info[i]
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
                                record_date = ts.datetime.fromtimestamp(int(
                                    item["submittime"]) / 1000).strftime(
                                    '%Y-%m-%d') if item["submittime"] else None
                            except:
                                record_date =None
                            # 裁判日期
                            try:
                                filing_date = ts.datetime.fromtimestamp(int(
                                    item["judgetime"]) / 1000).strftime(
                                    '%Y-%m-%d') if item["judgetime"] else None
                            except:
                                filing_date =None
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
                                'history': 0,
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
                            self.coll_5_1.insert_one(json_data)
                            if "_id" in json_data:
                                del json_data["_id"]
                            logger.success(f"司法数据保存成功:{json_data}!!")
                            logger.info(f"第 {page} 页数据！！")
                            self.send_data(3, json_data)
                            # break
                    else:
                        while True:
                            res = self.local_VQ_conn.lpop("sifaCookie")
                            if res is None:
                                print(">>>>>>>>>>>正在获取cookie信息.............")
                                time.sleep(1)
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
                                self.Nohishear(info, page)
                                break
                        break
                page+=1

            except Exception as e:
                logger.error(e)
                info["page"] = page
                self.col.insert_one(info)


    def fayuanhistroy(self, info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-judicial-risk/company/courtAnnouncement"
                params = {
                    "_": str(int(time.time() * 1000))
                }
                data = {
                    "pageSize": 10,
                    "pageNum": page,
                    "gid": info["id"],
                    "history": 0,
                    "identity": "-100",
                    "bltntypename": "-100",
                    "publishYear": "-100",
                    "reason": "-100",
                    "fullSearchText": ""
                }
                data = json.dumps(data, separators=(',', ':'))
                response = requests.post(url, headers=self.headers, params=params, data=data)
                print("【*】法院公告-->", response.json())
                if response.status_code == 200:
                    if response.json()["state"] == "ok" and response.json()['message'] == "":
                        num = math.ceil(int(response.json()["data"]['realTotal']) / 10) if response.json()["data"][
                            'realTotal'] else 0
                        logger.info(f'这个链接共{num}页数据')
                        logger.info(f'当前是第{page}页')
                        if page > num:
                            break
                        info_list = response.json()["data"]["list"]
                        for item in info_list:
                            item["companyName"] = info["company"]
                            self.coll_2.insert_one(item)
                            otherIdentity = []
                            if item['identityList']:
                                for li in item['identityList']:
                                    li_list = []
                                    for i in li['list']:
                                        if info["company"] in str(item['identityList']):
                                            if info["company"] in i['name']:
                                                ajsf = li['identity']
                                        else:
                                            ajsf =""
                                        if len(li['list']) > 1:
                                            name = i['name']
                                            li_list.append(name)
                                        else:
                                            name = li['list'][0]['name']
                                            li_list.append(name)
                                    data = {
                                        'identity': li['identity'],
                                        'list': li_list
                                    }
                                    otherIdentity.append(data)
                            else:
                                ajsf = ""
                                otherIdentity = "[]"
                            json_data = {
                                'relationCompanyName': info["company"],
                                'judicialType': '法院公告',
                                'history': 0,
                                'judicialUnit': item["courtcode"],
                                'recordDate': item['publishdate'],
                                'judicialName': '',
                                'judicialNumber': item['caseno'],
                                'filingDate': '',
                                'judicialMoney': '',
                                'infoType': item["bltntypename"],
                                'judicialContent': item['content'],
                                'sjmc': '',
                                'ajsf': ajsf,
                                'otherIdentity': otherIdentity,
                                'ay': item['reason'],
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
                            self.coll_2_1.insert_one(json_data)
                            if "_id" in json_data:
                                del json_data["_id"]
                            logger.success(f"司法数据保存成功:{json_data}!!")
                            logger.info(f"第 {page} 页数据！！")
                            self.send_data(3, json_data)
                            # break
                    else:
                        while True:
                            res = self.local_VQ_conn.lpop("sifaCookie")
                            if res is None:
                                print(">>>>>>>>>>>正在获取cookie信息.............")
                                time.sleep(1)
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
                                self.fayuanhistroy(info, page)
                                break
                        break
                page+=1
            except Exception as e:
                logger.error(e)
                info["page"]=page
                self.col.insert_one(info)

    # 被执行人
    def toryExecutors(self, info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-judicial-risk/risk/zhixing"
                params = {
                    "_": str(int(time.time() * 1000)),
                    "pageSize": "10",
                    "pageNum": page,
                    "gid": info["id"],
                    "keyword": ""
                }
                response = requests.get(url, headers=self.headers, params=params)
                print("【*】被执行人-->", response.json())
                if response.status_code == 200:
                    if response.json()["data"]:
                        if response.json()['message'] != "登录后可查看更多" and response.json()["errorCode"] == 0:
                            num = math.ceil(int(response.json()["data"]['count']) / 10) if \
                            response.json()["data"][
                                'count'] else 0
                            logger.info(f'这个链接共{num}页数据')
                            logger.info(f'当前是第{page}页')
                            if page > num:
                                break
                            info_list = response.json()["data"]["items"]
                            for item in info_list:
                                item["companyName"] = info["company"]
                                self.coll_6.insert_one(item)
                                # 相关案号
                                judicial_number = item["caseCode"] if item["caseCode"] else None
                                # 执行法院
                                judicial_unit = item["execCourtName"] if item["execCourtName"] else None
                                # 发布日期
                                record_date = ts.datetime.fromtimestamp(item["caseCreateTime"] / 1000) \
                                    .strftime('%Y-%m-%d') if item["caseCreateTime"] else None
                                # 判断是否为历史
                             
                                judicial_money = item["execMoney"] + "/元" if item["execMoney"] else None
                                bzxr = item["pname"] if item["pname"] else None
                                json_data = {
                                    'relationCompanyName': info["company"],
                                    'judicialType': '被执行人',
                                    'history': 0,
                                    'judicialUnit': judicial_unit,
                                    'recordDate': record_date,
                                    'judicialName': '',
                                    'judicialNumber': judicial_number,
                                    'filingDate': '',
                                    'judicialMoney': judicial_money,
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
                                    'sxSxxw': '',
                                    'sxLxqk': '',
                                    'jyYcrq': '',
                                    'jy_ycyy': '',
                                    'gqStatus': '',
                                }
                                self.coll_6_1.insert_one(json_data)
                                if "_id" in json_data:
                                    del json_data["_id"]
                                logger.success(f"司法数据保存成功:{json_data}!!")
                                logger.info(f"第 {page} 页数据！！")
                                self.send_data(3, json_data)
                                # break
                        else:
                            while True:
                                res = self.local_VQ_conn.lpop("sifaCookie")
                                if res is None:
                                    print(">>>>>>>>>>>正在获取cookie信息.............")
                                    time.sleep(1)
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
                                    self.toryExecutors(info, page)
                                    break
                            break
                    else:
                        break
                page+=1
            except Exception as e:
                logger.error(e)
                info["page"] = page
                self.col.insert_one(info)

    # 失信被执行人   恒大
    def jdefaulters(self,info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-judicial-risk/risk/dishonest"
                params = {
                    "_": str(int(time.time() * 1000)),
                    "keyWords": info["company"],
                    "pageSize": "10",
                    "pageNum": page,
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
                                num = math.ceil(int(json.loads(response.json()["data"])['total']) / 10) if json.loads(response.json()["data"])['total'] else 0
                                logger.info(f'这个链接共{num}页数据')
                                logger.info(f'当前是第{page}页')
                                if page > num:
                                    break
                                info_list = json.loads(response.json()["data"])["items"]
                                for item in info_list:
                                    item["companyName"] = info["company"]
                                    self.coll_7.insert_one(item)
                                    # 相关案号
                                    judicial_number = item["casecode"] if item["casecode"] else None
                                    # 执行法院
                                    judicial_unit = item["gistunit"] if item["gistunit"] else None
                                    # 发布日期
                                    record_date = ts.datetime.fromtimestamp(
                                        item["publishdate"] / 1000).strftime('%Y-%m-%d') if item[
                                        "publishdate"] else None
                                    # 立案日期
                                    filing_date = ts.datetime.fromtimestamp(
                                        item["regdate"] / 1000).strftime('%Y-%m-%d') if item["regdate"] else None
                                    # 判断是否为历史
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
                                    self.coll_7_1.insert_one(json_data)
                                    if "_id" in json_data:
                                        del json_data["_id"]
                                    logger.info(f"第 {page} 页数据！！")
                                    self.send_data(3, json_data)
                                    logger.success(f"司法数据保存成功:{json_data}!!")
                                    # break
                            else:
                                while True:
                                    res = self.local_VQ_conn.lpop("sifaCookie")
                                    if res is None:
                                        print(">>>>>>>>>>>正在获取cookie信息.............")
                                        time.sleep(1)
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
                                        self.jdefaulters(info, page)
                                        break
                                break
                        else:
                            break
                    elif response.json()["state"] == "warn":
                        break
                    else:
                        while True:
                            res = self.local_VQ_conn.lpop("sifaCookie")
                            if res is None:
                                print(">>>>>>>>>>>正在获取cookie信息.............")
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
                                self.jdefaulters(info, page)
                                break
                        break
                page+=1
            except Exception as e:
                logger.error(e)
                info["page"] = page
                self.col.insert_one(info)

    # 行政处罚
    def adminpen(self, info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-operating-risk/operating/punishment/punishIndexList"
                params = {
                    "withOwner": "0",
                    "_": str(int(time.time() * 1000)),
                    "pageSize": "10",
                    "pageNum": page,
                    "gid": info["id"]
                }
                response = requests.get(url, headers=self.headers, params=params)
                print("【*】行政处罚--->", response.json())
                if response.status_code == 200:
                    if response.json()['state'] == "ok" and response.json()['message'] == "":
                        num = math.ceil(int(response.json()["data"]["totalCount"]) / 10) if \
                        response.json()["data"][
                            "totalCount"] else 0
                        logger.info(f'这个链接共{num}页数据')
                        logger.info(f'当前是第{page}页')
                        if page > num:
                            break
                        info_list = response.json()["data"]["list"]
                        for item in info_list:
                                item["companyName"] = info["company"]
                                self.coll_8.insert_one(item)
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
                                self.coll_8_1.insert_one(json_data)
                                if "_id" in json_data:
                                    del json_data["_id"]
                                logger.success(f"司法数据保存成功:{json_data}!!")
                                logger.info(f"第 {page} 页数据！！")
                                self.send_data(3, json_data)
                                # break
                    else:
                        while True:
                            res = self.local_VQ_conn.lpop("sifaCookie")
                            if res is None:
                                print(">>>>>>>>>>>正在获取cookie信息.............")
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
                                self.adminpen(info, page)
                                break
                        break
                page+=1

            except Exception as e:
                logger.error(e)
                info["page"] = page
                self.col.insert_one(info)

    # 股权冻结  腾讯 恒大
    def equfreeze(self, info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-judicial-risk/risk/getJudicialList"
                params = {
                    "_": str(int(time.time() * 1000)),
                    "pageSize": "10",
                    "pageNum": page,
                    "gid": info["id"],
                    "sortType": "",
                    "identity": "",
                    "fullSearchText": ""
                }
                response = self.session.get(url, headers=self.headers, params=params)
                print("【*】股权冻结---->", response.json())
                if response.status_code == 200:
                    if response.json()["state"] == "ok":
                        if response.json()["data"]:
                            if response.json()['message'] == "":
                                num = math.ceil(int(response.json()["data"]["total"]) / 10) if response.json()["data"][
                                    "total"] else 0
                                logger.info(f'这个链接共{num}页数据')
                                logger.info(f'当前是第{page}页')
                                if page > num:
                                    break
                                info_list = response.json()["data"]["list"]
                                for item in info_list:
                                    item["companyName"] = info["company"]
                                    print(item)
                                    self.coll_9.insert_one(item)
                                    # 相关案号
                                    judicial_number = item["executeNoticeNum"] if item["executeNoticeNum"] else None
                                    # 执行法院
                                    judicial_unit = item["executiveCourt"] if item["executiveCourt"] else None
                                    # 发布日期
                                    record_date = item["publicityDate"] if bool(
                                        re.search(r"\d+", item["publicityDate"])) else None if item[
                                        "publicityDate"] else None
                                    # 判断是否为历史
                                  
                                    judicial_money = item["equityAmount"] if bool(
                                        re.search(r"\d+", item["publicityDate"])) else None if item[
                                        "equityAmount"] else None
                                    judicial_content = item["typeState"] if item["typeState"] else None
                                    bzxr = item["executedPerson"] if item["executedPerson"] else None
                                    json_data = {
                                        'relationCompanyName': info["company"],
                                        'judicialType': '股权冻结',
                                        'history': 0,
                                        'judicialUnit': judicial_unit,
                                        'recordDate': record_date,
                                        'judicialName': '',
                                        'judicialNumber': judicial_number,
                                        'filingDate': "",
                                        'judicialMoney': judicial_money,
                                        'infoType': "",
                                        'judicialContent': judicial_content,
                                        'sjmc': '',
                                        'ajsf': "",
                                        'otherIdentity': "[]",
                                        'ay': "",
                                        'sfDqslcx': '',
                                        'xfXfdx': '',
                                        'xfGldx': '',
                                        'xfSql': '',
                                        'bzxr': bzxr,
                                        'sxSxxw': "",
                                        'sxLxqk': "",
                                        'jyYcrq': '',
                                        'jy_ycyy': '',
                                        'gqStatus': '',
                                    }
                                    logger.info(json_data)
                                    self.coll_9_1.insert_one(json_data)
                                    if "_id" in json_data:
                                        del json_data["_id"]
                                    logger.success(f"司法数据保存成功:{json_data}!!")
                                    logger.info(f"第 {page} 页数据！！")
                                    self.send_data(3, json_data)
                                    # break
                            else:
                                while True:
                                    res = self.local_VQ_conn.lpop("sifaCookie")
                                    if res is None:
                                        print(">>>>>>>>>>>正在获取cookie信息.............")
                                        time.sleep(1)
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
                                        self.equfreeze(info, page)
                                        break
                                break
                        else:
                            break
                    else:
                        while True:
                            res = self.local_VQ_conn.lpop("sifaCookie")
                            if res is None:
                                print(">>>>>>>>>>>正在获取cookie信息.............")
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
                                self.equfreeze(info, page)
                                break
                        break
                page+=1
            except Exception as e:
                logger.error(e)
                info["page"] = page
                self.col.insert_one(info)


    # 经营异常  恒大
    def old_abnormal_data(self,info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-operating-risk/operating/abnormal/getAbnormalListByType"
                params = {
                    "_": str(int(time.time() * 1000)),
                    # "gid": info["id"],
                    "gid": info["id"],
                    "pageSize": "10",
                    "pageNum": page,
                    "abnormalType": "1"
                }
                response = self.session.get(url, headers=self.headers, params=params)
                print("【*】经营异常---->", response.json())
                if response.status_code == 200:
                    if response.json()["errorCode"] == 0:
                        if response.json()["data"]:
                            if response.json()['message'] != "登录后可查看更多":
                                num = math.ceil(int(response.json()["data"]['total']) / 10) if \
                                response.json()["data"][
                                    'total'] else 0
                                logger.info(f'这个链接共{num}页数据')
                                logger.info(f'当前是第{page}页')
                                if page > num:
                                    break
                                if not response.json()['data']:
                                    logger.info(f"【*】历史经营异常---->{response.json()}")
                                    break
                                info_list = response.json()["data"]["result"]
                                for item in info_list:
                                    item["companyName"] = info["company"]
                                    logger.info(item)
                                    self.coll_3.insert_one(item)
                                    # 执行法院
                                    judicial_unit = item["putDepartment"] if item["putDepartment"] else None
                                    # 发布日期
                                    record_date = item["putDate"] if item["putDate"] else None
                                    # 判断是否为历史
                                   
                                    judicial_content = item["putReason"] if item["putReason"] else None
                                    jy_ycrq = item["removeDate"] if item["removeDate"] else None
                                    jy_ycyy = item["removeReason"] if item["removeReason"] else None
                                    json_data = {
                                        'relationCompanyName': info["company"],
                                        'judicialType': '经营异常',
                                        'history':0,
                                        'judicialUnit': judicial_unit,
                                        'recordDate': record_date,
                                        'judicialName': '',
                                        'judicialNumber': "",
                                        'filingDate': "",
                                        'judicialMoney': "",
                                        'infoType': "",
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
                                        'jyYcrq': jy_ycrq,
                                        'jy_ycyy': jy_ycyy,
                                        'gqStatus': '',
                                    }
                                    logger.info(json_data)
                                    self.coll_3_1.insert_one(json_data)
                                    if "_id" in json_data:
                                        del json_data["_id"]
                                    logger.success(f"司法数据保存成功:{json_data}!!")
                                    logger.info(f"第 {page} 页数据！！")
                                    self.send_data(3, json_data)
                                    # break
                            else:
                                while True:
                                    res = self.local_VQ_conn.lpop("sifaCookie")
                                    if res is None:
                                        print(">>>>>>>>>>>正在获取cookie信息.............")
                                        time.sleep(1)
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
                                        self.old_abnormal_data(info, page)
                                        break
                                break
                        else:
                            break
                    else:
                        while True:
                            res = self.local_VQ_conn.lpop("sifaCookie")
                            if res is None:
                                print(">>>>>>>>>>>正在获取cookie信息.............")
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
                                self.old_abnormal_data(info, page)
                                break
                        break
                page+=1
            except Exception as e:
                logger.error(e)
                info["page"] = page
                self.col.insert_one(info)


    # 限制消费  恒大
    def Restrain(self, info,page):
        while True:
            try:
                url = "https://capi.tianyancha.com/cloud-judicial-risk/risk/getRestrictOrder"
                params = {
                    "_": str(int(time.time() * 1000)),
                    "gid": info["id"],
                    "pageSize": "10",
                    "pageNum": page
                }
                response = self.session.get(url, headers=self.headers, params=params)
                print("【*】限制消费---->", response.json())
                if response.status_code == 200:
                    if response.json()["errorCode"] == 0 and response.json()['message'] != "登录后可查看更多":
                        if response.json()["data"]:
                            num = math.ceil(int(response.json()["data"]['count']) / 10) if \
                            response.json()["data"][
                                'count'] else 0
                            logger.info(f'这个链接共{num}页数据')
                            logger.info(f'当前是第{page}页')
                            if page > num:
                                break
                            info_list = response.json()["data"]["items"]
                            for item in info_list:
                                    item["companyName"] = info["company"]
                                    self.coll_4.insert_one(item)
                                    # 相关案号
                                    judicial_number = item["caseCode"] if item["caseCode"] else None
                                    # 判断是否为历史
                                 
                                    # 执行法院
                                    judicial_unit = item["execCourtName"] if item["execCourtName"] else None
                                    # 发布日期
                                    record_date = item["publishDate"] if item["publishDate"] else None
                                    # 立案日期
                                    filing_date = ts.datetime.fromtimestamp(item["caseCreateTime"] / 1000) \
                                        .strftime('%Y-%m-%d') if item["caseCreateTime"] else None
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
                                    logger.info(f"第 {page} 页数据！！")
                                    self.send_data(3, json_data)
                                    # break
                        else:
                            break
                    else:
                        while True:
                            res = self.local_VQ_conn.lpop("sifaCookie")
                            if res is None:
                                print(">>>>>>>>>>>正在获取cookie信息.............")
                                time.sleep(1)
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
                                self.Restrain(info, page)
                                break
                        break
                page+=1
            except Exception as e:
                logger.error(e)
                info["page"] = page
                if "_id" in info:
                    del info["_id"]
                self.col.insert_one(info)
        self.local_0T_conn.sadd("sichuan:filter:cpws_com", info["company"])


    def send_data(self, flg, item):
        print("记录打点:", len(self.sfaj_item))
        if flg == 3:
            self.sfaj_item.append(item)
            if len(self.sfaj_item) >= 20:
                mongoToMQ(3, self.sfaj_item)
                logger.success(f"【*】发送成功：{self.sfaj_item}")
                self.sfaj_item.clear()


    def main(self):
        while True:
            try:
                res = self.local_VQ_conn.lpop("sifaCookie")
                if res is None:
                    print(">>>>>>>>>>>正在获取cookie信息.............")
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
                        obj_list = []
                        _ = 1
                        while True:
                            res = self.local_0T_conn.lpop("sichuan:company_id_02")
                            if res is None:
                                time.sleep(0.5)
                            else:
                                info = json.loads(res.decode("utf-8"))
                                if "_id" in info:
                                    del info['_id']
                                print(info)
                                try:
                                    if not self.local_0T_conn.sismember("sichuan:filter:cpws_com", info["company"]):
                                        # info = {"id": "7219966", 'company': "恒大地产集团有限公司"}
                                        # page_num=1
                                        # """法院公告"""
                                        # self.fayuanhistroy(info)
                                        obj =f.submit(self.fayuanhistroy,info=info,page=1)
                                        obj_list.append(obj)
                                        # page = 1
                                        # """经营异常"""
                                        # self.old_abnormal_data(info)
                                        obj1 =f.submit(self.old_abnormal_data, info=info,page=1)
                                        obj_list.append(obj1)
                                        # page = 1
                                        # """裁判文书"""
                                        # self.Nohishear(info)
                                        obj2 =f.submit(self.Nohishear, info=info,page=1)
                                        obj_list.append(obj2)
                                        # page = 1
                                        # """被执行人"""
                                        # self.toryExecutors(info)
                                        obj3 =f.submit(self.toryExecutors, info=info,page=1)
                                        obj_list.append(obj3)
                                        # page = 1
                                        # """失信被执行人"""
                                        # self.jdefaulters(info)
                                        obj4 =f.submit(self.jdefaulters, info=info,page=1)
                                        obj_list.append(obj4)
                                        # page = 1
                                        # """行政处罚"""
                                        # self.adminpen(info)
                                        obj5 =f.submit(self.adminpen, info=info,page=1)
                                        obj_list.append(obj5)
                                        # page = 1
                                        # """股权冻结"""
                                        # self.equfreeze(info)
                                        obj6 =f.submit(self.equfreeze, info=info,page=1)
                                        obj_list.append(obj6)
                                        # page = 1
                                        # """限制消费"""
                                        # self.Restrain(info)
                                        obj7 = f.submit(self.Restrain, info=info,page=1)
                                        obj_list.append(obj7)
                                    else:
                                        logger.warning(f"【*】司法已过滤:{info}")
                                    logger.info(f"。。。。。。。。。。。第{_}家公司")
                                    if len(obj_list) >= 200:
                                        for future in obj_list:
                                            try:
                                                future.result()
                                            except Exception as e:
                                                logger.error(e)
                                        obj_list.clear()
                                except Exception as e:
                                    logger.error(e)
                        for future in obj_list:
                            try:
                                future.result()
                            except Exception as e:
                                logger.error(e)
            except Exception as e:
                logger.error(e)


if __name__ == '__main__':
    sc = SuccessCODE()
    sc.main()