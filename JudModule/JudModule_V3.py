"""
@FileName：JudModule.py
@Description：
@Author：18k
@Time：2024/6/14 9:16
@Department：部门
@Website：站点
@Copyright：©2019-2024 职业
:return:
"""

import json
import math
import random
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from loguru import logger
from pymongo import MongoClient, ASCENDING, errors
from retrying import retry
from PikaUse import mongoToMQ
import requests
from config import checkconfig
from redis.client import Redis


class FLSS:

    def __init__(self,area):
        self.config = checkconfig(area)
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
        self.Request=None
        self.headers = None
        self.session=requests.session()
        self.ua=None

        self.cli_5 = self.client[self.config["rkey"]]["company_id"]
        self.cli = self.client[self.config["rkey"]]["sfaj"]
        self.cli_1 = self.client[self.config["rkey"]]["zlxx"]
        self.coll_2 = self.client_01[self.config["rkey"]]["司法案件"]
        self.coll_3 = self.client_01[self.config["rkey"]]["专利"]

        self.coll_2_1 = self.client_01[self.config["rkey"]]["fails_司法案件"]
        self.coll_2_1.create_index([("company", ASCENDING)], unique=True)

        self.coll_3_1 = self.client_01[self.config["rkey"]]["fails_专利"]
        self.coll_3_1.create_index([("company", ASCENDING)], unique=True)
        self.sfaj_item = list()
        self.zlxx_item = list()
        self.area_key=self.config["rkey"]+":company_id_03"
        self.sifa_filter_key=self.config["rkey"]+":filter:sfaj"
        self.zlxx_filter_key=self.config["rkey"]+":filter:zlxx_com"


    # 司法案件   已测试
    def sfaj(self,info,page):
        try:
            url = "https://capi.tianyancha.com/cloud-judicial-risk/judicialCase/list/v2"
            while True:
                params = {
                    "_": str(int(time.time() * 1000))}
                data = {
                    # "gid": 2343820668,
                    "gid": info["id"],
                    "pageSize": 10,
                    "pageNum": page,
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
                data = json.dumps(data, separators=(',', ':'))
                try:
                    response = self.session.post(url, headers=self.headers, params=params, data=data,proxies=self.Request["proxy"],timeout=(4,10))
                except Exception as e:
                    self.Request["proxy"] = self.proxy_list()
                    self.sfaj(info,page)
                    return
                logger.info('【***正在采集司法案件***】')
                print("司法数据>>>>>>>>>",response.text)
                if response.status_code == 200:
                    if response.json()["errorCode"]==0:
                        if response.json().get("data")["items"]:
                            num = math.ceil(int(response.json()['data']['count']) / 10) if response.json()['data'][
                                'count'] else 0
                            logger.info(f'这个链接共{num}页数据')
                            logger.info(f'当前是第{page}页')
                            if page > num:
                                break  # time.sleep(0.5)
                            info_list = response.json().get("data")["items"]
                            for item in info_list:
                                self.coll_2.insert_one(item)
                                # 关联公司名称
                                relation_company_name = info["company"]
                                # 案件名称
                                judicial_name = item["caseTitle"] if item[
                                    "caseTitle"] else None
                                # 相关案号
                                judicial_number = ",".join(
                                    i for i in item["caseCodeList"]) if item[
                                    "caseCodeList"] else None
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
                                    "history": 0,
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
                                self.cli.insert_one(info_item)
                                if "_id" in info_item:
                                    del info_item["_id"]
                                logger.success(f"司法数据保存成功:{info_item}!!")
                                logger.info(f"第 {page} 页数据！！")
                                self.send_data(3,info_item)
                        else:
                            break
                    else:
                        page += 1
                        while True:
                            res = self.local_VQ_conn.lpop("sifaCookie")
                            if res is None:
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
                                self.sfaj(info,page)
                                break
                        break
                page+=1
            self.local_conn.sadd(self.sifa_filter_key, info["company"])
        except Exception as e:
            logger.error(e)
            if "_id" in info:
                del info["_id"]
            self.Request["pchannel"] = random.randint(1, 6)
            self.Request["proxy"] = self.proxy_list()
            try:
                self.coll_2_1.insert_one(info)
                print("数据插入成功！")
            except errors.DuplicateKeyError:
                print("数据已存在，插入失败！")


    # 专利信息    已测试
    def zlxx(self, info,page):
        try:
            while True:
                url = "https://capi.tianyancha.com/cloud-intellectual-property/patent" \
                      "/patentListV6"
                params = {
                    "_": str(int(time.time() * 1000)),
                    "id": info["id"],
                    "pageSize": "10",
                    "pageNum": page,
                    "type": "-100",
                    "lprs": "-100",
                    "applyYear": "-100",
                    "pubYear": "-100",
                    "fullSearchText": "",
                    "sortField": "",
                    "sortType": "-100"}
                try:
                    response = self.session.get(url, headers=self.headers, params=params,proxies=self.Request["proxy"],timeout=(4,10))
                except Exception as e:
                    self.Request["proxy"] = self.proxy_list()
                    self.sfaj(info,page)
                    return
                logger.info('【***正在采集专利信息***】')
                print("专利数据>>>>>>>>>>>>>",response.json())
                if response.status_code == 200:
                    if response.json()["errorCode"] == 0:
                        num = math.ceil(int(response.json()['data']['viewtotal']) / 10) if response.json()['data'][
                            'viewtotal'] else 0
                        if page > num:
                            break
                        logger.info(f'这个链接共{num}页数据')
                        logger.info(f'当前是第{page}页')
                        info_list = response.json().get("data")["items"]
                        for patent_data in info_list:
                            self.coll_3.insert_one(patent_data)
                            property_title = patent_data["title"] if patent_data["title"] else None
                            # 申请号
                            property_num = patent_data["appnumber"] if patent_data["appnumber"] else None
                            # 申请日
                            try:
                                filing_date = datetime.strptime(patent_data["applicationTime"], "%Y-%m-%d").date() if \
                                    patent_data["applicationTime"] else None
                            except:
                                filing_date =None
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
                            # create_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                                "gainDate": patent_data["pubDate"] if patent_data["pubDate"] else None,
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
                            self.cli_1.insert_one(info_item)
                            logger.info(info_item)
                            if "_id" in info_item:
                                del info_item["_id"]
                            logger.info(f"第 {page} 页数据！！")
                            self.send_data(4, info_item)
                            logger.success(f"专利数据保存成功:{info_item}!!")
                    else:
                        while True:
                            res = self.local_VQ_conn.lpop("sifaCookie")
                            if res is None:
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
                                self.zlxx(info,page)
                                break
                        break
                page += 1
            self.local_conn.sadd(self.zlxx_filter_key, info["company"])
        except Exception as e:
            logger.error(e)
            if "_id" in info:
                del info["_id"]
            self.Request["pchannel"] = random.randint(1, 6)
            self.Request["proxy"] = self.proxy_list()
            try:
                self.coll_3_1.insert_one(info)
                print("数据插入成功！")
            except errors.DuplicateKeyError:
                print("数据已存在，插入失败！")

    @retry(wait_fixed=1000)
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
                resp = requests.get("https://myip.ipip.net", proxies=proxies,timeout=4)
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

    def send_data(self,flg,item):
        print("记录打点:",len(self.sfaj_item))
        if flg==3:
            self.sfaj_item.append(item)
            if len(self.sfaj_item) >= 20:
                logger.info(self.sfaj_item)
                mongoToMQ(3, self.sfaj_item)
                logger.success(f"【*】发送成功：{self.sfaj_item}")
                self.sfaj_item.clear()
        if flg==4:
            self.zlxx_item.append(item)
            if len(self.zlxx_item) >= 20:
                logger.info(self.zlxx_item)
                mongoToMQ(4, self.zlxx_item)
                logger.success(f"【*】发送成功：{self.zlxx_item}")
                self.zlxx_item.clear()

    # 运行函数
    def run(self):
        while True:
            res = self.local_VQ_conn.lpop("sifaCookie")
            if res is None:
                print(">>>>>>>>>>>>>>>>>>正在获取cookie信息................")
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
                    all_list = []
                    _ = 1
                    while True:
                        res = self.local_conn.lpop(self.area_key)
                        if res is None:
                            time.sleep(0.5)
                        else:
                            company_id = json.loads(res.decode("utf-8"))
                            if "_id" in company_id:
                                del company_id['_id']
                            print(company_id)
                            if not  self.local_conn.sismember(self.sifa_filter_key,company_id["company"]):
                                    sf_future=f.submit(self.sfaj,info=company_id,page=1)
                                    all_list.append(sf_future)
                            else:
                                logger.warning(f"【*】司法已过滤:{company_id}")
                            if not  self.local_conn.sismember(self.zlxx_filter_key,company_id["company"]):
                                    zl_future=f.submit(self.zlxx, info=company_id,page=1)
                                    all_list.append(zl_future)
                            else:
                                logger.warning(f"【*】专利已过滤:{company_id}")
                            logger.info(f"。。。。。。。。。。。第{_}家公司")
                            _ += 1
                            if len(all_list) >= 30:
                                for gg in all_list:
                                    try:
                                        gg.result()
                                    except Exception as e:
                                        logger.error(e)
                                        gg.result()
                                all_list.clear()
                    for gg in all_list:
                        try:
                            gg.result()
                        except Exception as e:
                            logger.error(e)
                            gg.result()
                    break



if __name__ == '__main__':
    FLSS("qinghai").run()