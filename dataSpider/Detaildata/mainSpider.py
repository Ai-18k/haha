"""
@FileName：mainSpider.py
@Description：
@Author：18k
@Time：2024/6/1.txt 20:52
@Department：部门
@Website：站点
@Copyright：©2019-2024 职业
:return:
"""

import pika
import pymongo
from lxml import etree
from retrying import retry
from ParseFile.parsehtml import  parasHTML
import json
import re
import time
import redis
import requests
from loguru import logger
from RiskcontrolPass.passSpan import Test
from datetime import datetime


class Login_module:

    def __init__(self):
        self.session = requests.Session()
        self.conn = redis.Redis(host='182.43.38.79', port=6379, db=5, password="lzh990130",socket_connect_timeout=70)
        self.client = pymongo.MongoClient(host='192.168.5.167', port=27017)
        self.client_01 = pymongo.MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",
                                     authSource="admin")
        self.local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=70)
        self.coli = self.client["fujian"]["2nf_add_company_id"]

        self.coll_2 = self.client_01["company"]["zhejiang"]["company"]
        self.coll = self.client["fujian"]["company"]
        self.coll_1 = self.client["fujian"]["company_with"]
        self.coli = self.client["fujian"]["company_id"]
        self.collection_2 = self.client["fujian"]["company_qualification"]
        self.collection_3 = self.client["fujian"]["fail_company"]
        self.collection_4 = self.client["fujian"]["fail_company_with"]
        self.collection_5 = self.client["fujian"]["fail_qualification"]
        self.collection_6 = self.client["fujian"]["fail_company_id"]
        self.coll1 = self.client["fujian"]["公司详情失败公司id"]
        self.finger = ["chrome99", "chrome100", "chrome101", "chrome104", "chrome107",
                       "chrome110", "chrome116", "chrome119", "chrome120", "edge99",
                       "edge101", "safari15_3",
                       "safari15_5", "safari17_0", "chrome99"]
        self.Reqest = {}
        self.data_item = list()
        self.data1_item=list()
        self.data2_item=list()
        self.p_str = "16_18"
        self.area = "fujian"
        # self.res=list(self.coli.find())
        # self.filter = "filter:serv_company"

    @retry(wait_fixed=1000)
    def get_data(self, info):
        try:
            self.session.cookies.set("auth_token", self.Reqest["token"])
            self.session.cookies.set("ssuid", self.Reqest["userid"])
            self.session.cookies.set("searchSessionId", self.Reqest["sessionNo"])
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "DNT": "1.txt",
                "Pragma": "no-cache",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                # "Referer": "https://www.tianyancha.com/search?key=&base=fj&cacheCode={}&sessionNo={}".format(
                #     info['areaCode'], self.Reqest["sessionNo"]),
                "Referer": "https://www.tianyancha.com/login?from=%2Fcompany%2F{}".format(info["id"]),
                "Sec-Fetch-User": "?1.txt",
                "Upgrade-Insecure-Requests": "1.txt",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\""
            }
            url = "https://www.tianyancha.com/company/{}".format(info["id"])
            response = self.session.get(url, headers=headers)
            logger.info(url)
            logger.info(self.Reqest["mobil"])
            logger.info(info)
            logger.info(response.status_code)
            # print(response.text)
            if response.status_code == 200:
                if "若您使用的是兼容模式，需切换至" in response.text:
                    item_info = parasHTML(response.text, info["id"])
                    print("html解析")
                    data1 = (0, 1, item_info["create_datetime"], None, None, None, None,
                             item_info["company_name"], None, item_info["nameLevel2"], None,
                             item_info["nameLevel1"])
                    logger.info(data1)
                    data2 = (0, item_info["short_name"], item_info["company_name"],
                             item_info["legal_name"], item_info["legal_telephone"], None,
                             item_info["company_address"], 2, item_info["registered_address"],
                             item_info["company_phone"], item_info["staff_size"],
                             item_info["create_by"], item_info["create_datetime"], None, None, 0,
                             item_info["date_of_establishment"], item_info["registered_capital"],
                             item_info["contributed_capital"], item_info["business_scope"],
                             item_info["registration_status"], item_info["tyxydm"],
                             item_info["gszch"], item_info["nsrsbh"], item_info["zzjgdm"],
                             item_info["nsrzz"], item_info["yyqx"], item_info["company_type"],
                             item_info["registration_authority"])
                    logger.info(data2)
                    self.coll_1.insert_one({
                        'keys': data1})
                    self.coll.insert_one({
                        'keys': data2})
                    self.conn.sadd("filter:serv_company",item_info["company_name"])
                    self.conn.lpush("copy_done_company_id", json.dumps(info))
                    if len(self.data2_item) >= 20:
                        self.sendToMQ(2, self.data2_item)
                        self.data2_item.clear()
                    if len(self.data1_item) >= 20:
                        self.sendToMQ(1, self.data1_item)
                        self.data1_item.clear()
                    if len(self.data_item) >= 20:
                        self.sendToMQ(0, self.data_item)
                        self.data_item.clear()
                    with open("info.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    logger.success(data1)
                    logger.success(data2)
                    raise Exception("未找到企业资质！！请查看info.html")
                elif '<script id="__NEXT_DATA__" type="application/json">' in response.text:
                    logger.info("数据正常解析!!")
                    html = etree.HTML(response.text)
                    job_time = "".join(i for i in (
                        html.xpath('//tbody/tr[6]/td[2]/span/text()'))) if html.xpath(
                        '//tbody/tr[6]/td[2]/span/text()') else None
                    json_date = json.loads(html.xpath('//script[@id="__NEXT_DATA__"]/text()')[0])
                    data = json_date["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"][
                        "data"]
                    self.coll_2.insert_one(data)
                    item_info = dict()
                    item_info["short_name"] = data["alias"] if data["alias"] else None
                    item_info["company_name"] = data["name"] if data["name"] else None
                    item_info["legal_name"] = data["legalPersonName"] if data["legalPersonName"] else None
                    if "legalPersonId" in data:
                        item_info["legal_telephone"] = data["legalPersonId"] if data[
                            "legalPersonId"] else None
                    else:
                        item_info["legal_telephone"] = None
                    item_info["company_address"] = data["regLocation"] if data[
                        "regLocation"] else None
                    item_info["registered_address"] = data["regLocation"] if data[
                        "regLocation"] else None
                    if "taxPhone" in data:
                        item_info["company_phone"] = \
                            [num.strip() if "****" not in num else ""
                             for num in str(data["taxPhone"]).split(";")][0] if data[
                                "taxPhone"] else ""
                    else:
                        item_info["company_phone"] = None

                    if "staffNumInfo" in data:
                        item_info["staff_size"] = data["staffNumInfo"]["num"] if data[
                            "staffNumInfo"] else None
                    else:
                        item_info["staff_size"] = None
                    item_info["create_by"] = 1
                    item_info[
                        "create_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    try:
                        if "estiblishTime" in data:
                            item_info["date_of_establishment"] = datetime.fromtimestamp(data["estiblishTime"] / 1000.0) if data["estiblishTime"] else None
                        else:
                            item_info["date_of_establishment"] = None
                    except:
                        item_info["date_of_establishment"] = None
                    item_info["registered_capital"] = data["regCapital"] if data[
                        "regCapital"] else None

                    item_info["contributed_capital"] = data["actualCapital"] if data[
                        "actualCapital"] else None
                    if "businessScope" in data:
                        item_info["business_scope"] = data["businessScope"] if data[
                            "businessScope"] else None
                    else:
                        item_info["business_scope"] = None
                    item_info["registration_status"] = data["regStatus"] if data[
                        "regStatus"] else None
                    if "creditCode" in data:
                        item_info["tyxydm"] = data["creditCode"] if data[
                            "creditCode"] else None
                    else:
                        item_info["tyxydm"] = None
                    if "regNumber" in data:
                        item_info["gszch"] = data["regNumber"] if data[
                            "regNumber"] else None
                    else:
                        item_info["gszch"] = None

                    item_info["nsrsbh"] = data["companyCreditCode"] if data[
                        "companyCreditCode"] else None
                    if "orgNumber" in data:
                        item_info["zzjgdm"] = data["orgNumber"] if data[
                            "orgNumber"] else None
                    else:
                        item_info["zzjgdm"] = None
                    # 详情页
                    #   item_info["company_id"] = data["id"]
                    item_info["yyqx"] = job_time

                    # 行业类型  类别
                    if data["industryInfo"]:
                        industryInfo = data["industryInfo"]
                        if "nameLevel2" in industryInfo:
                            item_info["nameLevel2"] = industryInfo["nameLevel2"]
                            item_info["nameLevel1"] = industryInfo["nameLevel1"]
                        else:
                            if "nameLevel1" in industryInfo:
                                if industryInfo["nameLevel1"]:
                                    item_info["nameLevel1"] = industryInfo["nameLevel1"]
                                    item_info["nameLevel2"] = None
                                else:
                                    item_info["nameLevel2"] = None
                                    item_info["nameLevel1"] = None
                    else:
                        item_info["nameLevel1"] = None
                        item_info["nameLevel2"] = None
                    # nameLevel3=industryInfo["nameLevel3"]
                    # 注册地址
                    if "regInstitute" in data:
                        item_info["registration_authority"] = data["regInstitute"] \
                            if \
                            data[
                                "regInstitute"] else None
                    else:
                        item_info["registration_authority"] = None

                    # 企业资质
                    if "taxQualification" in data:
                        item_info["nsrzz"] = data["taxQualification"] if data[
                            "taxQualification"] else None
                    else:
                        item_info["nsrzz"] = None

                    # 企业资质
                    if "companyShowBizTypeName" in data:
                        item_info["company_type"] = data["companyShowBizTypeName"] \
                            if \
                            data["companyShowBizTypeName"] else None
                    else:
                        item_info["company_type"] = None

                    if "tagListV2" in data:
                        for tag in data["tagListV2"]:
                            self.collection_2.insert_one({"relationCompanyName": data["name"], "relationQualificationName":
                                    tag["name"]})
                            self.data2_item.append({"relationCompanyName": data["name"], "relationQualificationName":
                                tag["name"]})
                            logger.success({"relationCompanyName": data["name"], "relationQualificationName":tag["name"]})
                    if item_info['date_of_establishment']:
                        date_of_establishment = item_info["date_of_establishment"].strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        date_of_establishment = None
                    item_info.update({'date_of_establishment': date_of_establishment})
                    self.data_item.append({
                        "shortName": item_info["short_name"],
                        "companyName": item_info["company_name"],
                        "legalName": item_info["legal_name"],
                        "legalTelephone": item_info["legal_telephone"],
                        "companyAddress": item_info["company_address"],
                        "registeredAddress": item_info["registered_address"],
                        "companyPhone": item_info["company_phone"],
                        "staffSize": item_info["staff_size"],
                        "dateOfEstablishment": item_info["date_of_establishment"],
                        "registeredCapital": item_info["registered_capital"],
                        "contributedCapital": item_info["contributed_capital"],
                        "businessScope": item_info["business_scope"],
                        "registrationStatus": item_info["registration_status"],
                        "tyxydm": item_info["tyxydm"],
                        "nsrsbh": item_info["nsrsbh"],
                        "zzjgdm": item_info["zzjgdm"],
                        "yyqx": item_info["yyqx"],
                        "companyType": item_info["company_type"],
                        "registrationAuthority": item_info["registration_authority"],
                        "gszch": item_info["gszch"],
                        "nsrzz": item_info["nsrzz"],
                        "provincialScope": None,
                        # "city": None,
                        # "areaCode": None
                        "city": info['city'],
                        "areaCode": info['areaCode']
                    })
                    self.data1_item.append({
                        "relationCompanyName": item_info["company_name"],
                        "relationIndustryName": item_info["nameLevel2"],
                        "relationIndustryPname": item_info["nameLevel1"],
                    })
                    data1 = (0, 1, item_info["create_datetime"], None, None, None, None,
                             item_info["company_name"], None, item_info["nameLevel2"], None,
                             item_info["nameLevel1"])
                    logger.info(data1)
                    data2 = (0, item_info["short_name"], item_info["company_name"],
                             item_info["legal_name"], item_info["legal_telephone"], None,
                             item_info["company_address"], 2, item_info["registered_address"],
                             item_info["company_phone"], item_info["staff_size"],
                             item_info["create_by"], item_info["create_datetime"], None, None, 0,
                             item_info["date_of_establishment"], item_info["registered_capital"],
                             item_info["contributed_capital"], item_info["business_scope"],
                             item_info["registration_status"], item_info["tyxydm"],
                             item_info["gszch"], item_info["nsrsbh"], item_info["zzjgdm"],
                             item_info["nsrzz"], item_info["yyqx"], item_info["company_type"],
                             item_info["registration_authority"]
                             ,info['city'],info['areaCode']
                             )
                    logger.info(data2)
                    self.coll_1.insert_one({'keys': data1})
                    self.coll.insert_one({'keys': data2})
                    self.local_conn.sadd("filter:company", item_info["company_name"])
                    if len(self.data2_item) >= 20:
                        logger.info(len(self.data2_item))
                        self.sendToMQ(2, self.data2_item)
                        self.data2_item.clear()
                    if len(self.data1_item) >= 20:
                        logger.info(len(self.data1_item))
                        self.sendToMQ(1, self.data1_item)
                        self.data1_item.clear()
                    if len(self.data_item) >= 20:
                        logger.info(len(self.data_item))
                        self.sendToMQ(0, self.data_item)
                        self.data_item.clear()
                    logger.success(data1)
                    logger.success(data2)
                else:
                    while True:
                        res = self.conn.lpop("searchCookie")
                        if res is None:
                            time.sleep(2)
                        else:
                            self.Reqest = json.loads(res.decode("utf-8"))
                            print(self.Reqest)
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Reqest["cookie_dict"])
                            raise Exception("失效")
            elif response.status_code == 429:
                refer = re.findall("访问网址：(.*?)</li>", response.text, re.S)[0]
                t_is = Test(response.text, self.session).validate_jy(refer)
                if t_is:
                    logger.success("状态刷新成功！！恢复采集....")
                    raise Exception("状态刷新")
            elif response.status_code == 404:
                logger.error(f"{info}：页面不存在!")
            else:
                while True:
                    res = self.conn.lpop("searchCookie")
                    if res is None:
                        time.sleep(2)
                    else:
                        self.Reqest = json.loads(res.decode("utf-8"))
                        print(self.Reqest)
                        self.session.cookies = requests.utils.cookiejar_from_dict(self.Reqest["cookie_dict"])
                        raise Exception("失效")
        except:
            self.coll1.insert_one(info)


    def sendToMQ(self, flg, item_info):
        credentials = pika.PlainCredentials('user', 'user123')  # 用户名和密码
        parameters = pika.ConnectionParameters(host='139.9.70.234',
                                               # RabbitMQ服务器地址
                                               port=5672,
                                               # RabbitMQ服务器端口，默认是5672
                                               virtual_host='/',
                                               # 虚拟主机，默认是'/'
                                               credentials=credentials
                                               # 用户名和密码
                                               )
        # 创建一个到RabbitMQ服务器的连接
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channe2 = connection.channel()
        channe3 = connection.channel()

        # 创建一个队列，如果不存在的话
        channel.queue_declare(queue='qqbx.dc.company', durable=True)
        channe2.queue_declare(queue='qqbx.dc.industry', durable=True)
        channe3.queue_declare(queue='qqbx.dc.qualification', durable=True)

        if flg == 0:
            try:
                # 发送消息到队列
                channel.basic_publish(exchange='', routing_key='qqbx.dc.company', body=json.dumps(item_info))
                logger.success(f"公司工商详情:{item_info} 发送成功！！")
            except Exception as e:
                self.collection_3.insert_one(item_info)
        elif flg == 1:
            try:
                channe2.basic_publish(exchange='',
                                      routing_key='qqbx.dc.industry', body=json.dumps(item_info))
                logger.success(f"公司关联数据:{item_info} 发送成功！！")
            except Exception as e:
                self.collection_4.insert_one(item_info)
        else:
            try:
                channe3.basic_publish(exchange='', routing_key='qqbx.dc.qualification', body=json.dumps(item_info))
                logger.success(f"企业资质信息:{item_info} 发送成功！！")
            except Exception as e:
                self.collection_5.insert_one(item_info)
        connection.close()

    # @retry(wait_fixed=1000)
    # def main(self):
    #     while True:
    #         res = self.conn.lpop("searchCookie")
    #         # res = self.conn.get("searchCookie")
    #         if res is None:
    #             time.sleep(10)
    #         else:
    #             self.Reqest = json.loads(res.decode("utf-8"))
    #             print(self.Reqest)
    #             self.session.cookies = requests.utils.cookiejar_from_dict(self.Reqest["cookie_dict"])
    #             _ = 1.txt
    #             # _ = int(self.conn.get("num2"))
    #             comset = set()
    #             with ThreadPoolExecutor(3) as f:
    #                 while True:
    #                     # res = self.conn.lpop(f"{self.area}:{self.p_str}:company_id")
    #                     res = self.conn.lpop("add_ID")
    #                     if res is None:
    #                         time.sleep(0.5)
    #                     else:
    #             # result = self.coli.find()
    #             # for info in list(result)[_:]:
    #                         info = json.loads(res.decode("utf-8"))
    #                         # del info['_id']
    #                         print(info)
    #                         p_filter = info["company"] + str(info["id"])
    #                         if p_filter not in info:
    #                             # f.submit(self.get_data, info=info)
    #                             self.get_data(info)
    #                         else:
    #                             logger.warning(f"【*】公司id已过滤:{info}")
    #                         comset.add(p_filter)
    #                         if len(comset) > 10000:
    #                             comset.clear()
    #                         logger.info("第{}页".format(_))
    #                         self.conn.set("1_num", _)
    #                         if _ == 10000:
    #                             logger.success("已完成采集!!")
    #                             break
    #                         _ += 1.txt

    def main(self):
        while True:
            res = self.conn.lpop("searchCookie")
            if res is None:
                time.sleep(2)
            else:
                self.Reqest = json.loads(res.decode("utf-8"))
                print(self.Reqest)
                self.session.cookies = requests.utils.cookiejar_from_dict(self.Reqest["cookie_dict"])
                _ = int(self.conn.get("3M_detail_num"))
                # with ThreadPoolExecutor(3) as f:
                for info in list(self.res[_:]):
                    if "_id" in info:
                        del info['_id']
                    print(info)
                    if not self.local_conn.sismember("filter:company",info["company"]):
                        # f.submit(self.get_data, info=info)
                        self.get_data(info)
                    else:
                        logger.warning(f"【*】公司存在已过滤:{info}")
                    logger.info("。。。。。。。。。。。。。。第{}家数据".format(_))
                    self.conn.set("3M_detail_num", _)
                    _ += 1


if __name__ == '__main__':
    ll = Login_module()
    ll.main()

