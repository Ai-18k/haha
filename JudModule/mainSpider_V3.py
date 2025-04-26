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
import os
import random
from concurrent.futures import ThreadPoolExecutor
import pika
from pymongo import MongoClient, WriteConcern
from lxml import etree
from retrying import retry
from autoPass import main
from pause_html import parasHTML
import json
import re
import time
import redis
import requests
from loguru import logger
from datetime import datetime


class Login_module:
    #
    def __init__(self):
        self.session = requests.session()
        self.client = MongoClient(host='192.168.5.167', port=27017)
        self.client_01 = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",
                                     authSource="admin")
        self.local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=1170)
        self.local_VQ_conn = redis.Redis(host='192.168.5.181', port=7933, db=0, password="fer@nhaweif576KUG",
                                         socket_connect_timeout=1170)
        self.coll_2 = self.client_01["company"]["qinghai"]["company"]
        self.coll = self.client["qinghai"]["company"]
        self.coll_1 = self.client["qinghai"]["company_with"]
        self.coli = self.client["qinghai"]["company_id"]
        self.collection_2 = self.client["qinghai"]["company_qualification"]
        self.collection_3 = self.client["qinghai"]["fail_company"]
        self.collection_4 = self.client["qinghai"]["fail_company_with"]
        self.collection_5 = self.client["qinghai"]["fail_qualification"]
        self.collection_6 = self.client["qinghai"]["fail_company_id"]
        self.coll1 = self.client["qinghai"]["公司详情失败公司id"]
        self.finger = ["chrome99", "chrome100", "chrome101", "chrome104", "chrome107",
                       "chrome110", "chrome116", "chrome119", "chrome120", "edge99",
                       "edge101", "safari15_3",
                       "safari15_5", "safari17_0", "chrome99"]
        self.Reqest = {}
        self.data_item = list()
        self.data1_item=list()
        self.data2_item=list()
        self.write_concern = WriteConcern(w=1)

    def proxy_list(self):
        # 隧道域名:端口号
        tunnel = "d152.kdltps.com:15818"
        # 用户名密码方式
        username = "t13206952228334"
        password = "wtx4i2in:%d" % random.randint(1, 5)
        proxies = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
        }
        # resp = requests.get("https://myip.ipip.net", proxies=proxies)
        # if resp.status_code == 200:
        #     print(resp.text)
        return proxies

    @retry(wait_fixed=100)
    def get_data(self, info):
        # try:
            self.session.cookies.set("auth_token", self.Reqest["token"])
            self.session.cookies.set("searchSessionId","{:.8f}".format(time.time()))
            self.session.cookies.set("Hm_lpvt_e92c8d65d92d534b0fc290df538b4758", str(int(time.time())))
            headers = {
                "Host": "www.tianyancha.com",
                "Cache-Control": "max-age=0",
                "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1",
                "User-Agent":self.Reqest["ua"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Referer": "https://www.tianyancha.com/company/%s" % info["id"],
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            url = "https://www.tianyancha.com/company/%s" % str(info["id"])
            response =self.session.get(url, headers=headers, proxies=self.proxy_list())
            logger.info(url)
            logger.info(self.Reqest["mobil"])
            logger.info(info)
            logger.info(response.status_code)
            if response.status_code == 200:
                match01 = re.search(r'<script[^>]*id=["\']__NEXT_DATA__["\'][^>]*>', response.text, re.S)
                if not match01:
                    if "若您使用的是兼容模式，需切换至" in response.text:
                        item_info = parasHTML(response.text, info)
                        print("html解析")
                        data1 = (0, 1, item_info["create_datetime"], None, None, None, None,
                                 item_info["companyName"], None, item_info["nameLevel2"], None,
                                 item_info["nameLevel1"])
                        logger.info(data1)
                        data2 = (0, item_info["shortName"], item_info["companyName"],
                                 item_info["legalName"], item_info["legalTelephone"], None,
                                 item_info["companyAddress"], 2, item_info["registeredAddress"],
                                 item_info["companyPhone"], item_info["staffSize"],
                                 1, item_info["create_datetime"], None, None, 0,
                                 item_info["dateOfEstablishment"], item_info["registeredCapital"],
                                 item_info["contributedCapital"], item_info["businessScope"],
                                 item_info["registrationStatus"], item_info["tyxydm"],item_info["shzzlx"],
                                 item_info["gszch"], item_info["nsrsbh"], item_info["zzjgdm"],
                                 item_info["nsrzz"], item_info["yyqx"], item_info["companyType"],
                                 item_info["registrationAuthority"],info["id"],info["areaCode"],None)
                        self.data1_item.append({
                            "relationCompanyName": None,
                            "relationIndustryName": item_info["nameLevel2"],
                            "relationIndustryPname": item_info["nameLevel1"],
                        })
                        del item_info["nameLevel2"]
                        del item_info["nameLevel1"]
                        self.data_item.append(item_info)
                        logger.info(data2)
                        self.coll_1.with_options(write_concern=self.write_concern).insert_one({
                            'keys': data1})
                        self.coll.with_options(write_concern=self.write_concern).insert_one({
                            'keys': data2})
                        self.local_conn.sadd("qinghai:filter:company",info["company"])
                        if len(self.data2_item) >= 20:
                            self.sendToMQ(2, self.data2_item)
                            self.data2_item.clear()
                        if len(self.data1_item) >= 20:
                            self.sendToMQ(1, self.data1_item)
                            self.data1_item.clear()
                        if len(self.data_item) >= 20:
                            self.sendToMQ(0, self.data_item)
                            self.data_item.clear()
                        file_path =os.path.join("html","info_%s.html" % str(info["id"]))
                        # 如果文件夹不存在则创建
                        if not os.path.exists("html"):
                            os.makedirs("html")
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(response.text)
                        self.local_conn.lpush("qinghai:fail:detailHtml", json.dumps(info))
                    else:
                        while True:
                            res = self.local_VQ_conn.lpop("detailCookie")
                            if res is None:
                                time.sleep(1)
                            else:
                                self.Reqest = json.loads(res.decode("utf-8"))
                                print(self.Reqest)
                                self.session.cookies = requests.utils.cookiejar_from_dict(self.Reqest["cookie_dict"])
                                raise Exception("失效")
                else:
                    logger.info("数据正常解析!!")
                    html = etree.HTML(response.text)
                    job_time = "".join(i for i in (
                        html.xpath('//tbody/tr[6]/td[2]/span/text()'))) if html.xpath(
                        '//tbody/tr[6]/td[2]/span/text()') else None
                    json_date = json.loads(html.xpath('//script[@id="__NEXT_DATA__"]/text()')[0])
                    data = json_date["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"][
                        "data"]
                    self.local_conn.sadd("qinghai:filter:company", data["name"])
                    self.coll_2.with_options(write_concern=self.write_concern).insert_one(data)
                    item_info = dict()
                    item_info["short_name"] = data["alias"] if data["alias"] else None

                    hnlist = list()
                    if "historyNames" in data:
                        logger.info("历史名称:------->{}".format(data["historyNames"]))
                        if "\n" in data["historyNames"]:
                            hnlist = str(data["historyNames"]).split("\n")
                        else:
                            hnlist.append(data["historyNames"])
                    else:
                        hnlist = list()
                    item_info["historyNames"] = hnlist

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
                    if "types" in data:
                        item_info["type"] = data["types"] if data["types"] else None
                    else:
                        item_info["type"] = None
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
                            self.collection_2.with_options(write_concern=self.write_concern).insert_one({"relationCompanyName": data["name"], "relationQualificationName":
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
                        # 20241029新添加"shzzlx"
                        "shzzlx": item_info["type"],
                        "nsrzz": item_info["nsrzz"],
                        "provincialScope": None,
                        # "city": None,
                        # "areaCode": None
                        "city": info['city'],
                        "areaCode": info['areaCode'],
                        "oldCompanyNameList": item_info["historyNames"],
                        "dataSource":1
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
                             item_info["registration_status"], item_info["tyxydm"],item_info["type"],
                             item_info["gszch"], item_info["nsrsbh"], item_info["zzjgdm"],
                             item_info["nsrzz"], item_info["yyqx"], item_info["company_type"],
                             item_info["registration_authority"]
                             ,info['city'],info['areaCode'],item_info["historyNames"]
                             )
                    logger.info(data2)
                    self.coll_1.with_options(write_concern=self.write_concern).insert_one({'keys': data1})
                    self.coll.with_options(write_concern=self.write_concern).insert_one({'keys': data2})
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
            elif response.status_code == 406 or "系统检测到您当前帐号的操作存在异常" in response.text:
                logger.error("{}：账号封禁！！".format(self.Reqest["mobil"]))
                if 'keys' in self.Reqest["mobil"]:
                    logger.info(self.Reqest["mobil"])
                    keys = self.Reqest["mobil"]["keys"]
                    del self.Reqest["mobil"]["keys"]
                    logger.info(keys)
                    self.local_VQ_conn.sadd("ErrorMobil", json.dumps(self.Reqest["mobil"]))
                    self.local_VQ_conn.lrem(keys, 1, json.dumps(self.Reqest["mobil"]))
                else:
                    self.local_VQ_conn.sadd("ErrorMobil", json.dumps(self.Reqest["mobil"]))
                    self.local_VQ_conn.lrem("memeryUser", 1, json.dumps(self.Reqest["mobil"]))
                while True:
                    res = self.local_VQ_conn.lpop("detailCookie")
                    if res is None:
                        time.sleep(1)
                    else:
                        self.Reqest = json.loads(res.decode("utf-8"))
                        print(self.Reqest)
                        # self.session.cookies = requests.utils.cookiejar_from_dict(self.Reqest["cookie_dict"])
                        raise Exception("账号封禁！！")
            elif response.status_code == 429 or "请进行身份验证以继续使用" in response.text:
                # refer = re.findall("访问网址：(.*?)</li>", response.text, re.S)[0]
                # content = {"content": response.text, "refer": refer,
                #            "cookie": requests.utils.dict_from_cookiejar(self.session.cookies), "UA": headers,
                #            "company": info["company"], "id": info["id"]}
                # self.local_conn.lpush("safe_verify", json.dumps(content))
                # while True:
                #     is_run = self.local_conn.lpop("is_safe")
                #     time.sleep(4)
                #     if is_run is None:
                #         print("超时")
                #         raise Exception("状态刷新失败")
                #     else:
                #         if is_run.decode():
                #             logger.success("状态刷新成功！！恢复采集....")
                #             raise Exception("状态刷新")
                #         else:
                #             logger.error("状态刷新失败")
                #             raise Exception("状态刷新失败")
                cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
                _isPass = main(cookies, headers)
                if _isPass:
                    logger.success("状态刷新成功！！")
                    raise Exception("重试")
                else:
                    logger.warning("状态异常！！")
                    raise Exception("重试")
            elif response.status_code == 404:
                logger.error(f"{info}：页面不存在")
            else:
                logger.info(response.text)
                while True:
                    res = self.local_VQ_conn.lpop("detailCookie")
                    if res is None:
                        time.sleep(1)
                    else:
                        self.Reqest = json.loads(res.decode("utf-8"))
                        print(self.Reqest)
                        # self.session.cookies = requests.utils.cookiejar_from_dict(self.Reqest["cookie_dict"])
                        raise Exception("失效")
        # except Exception as e:
        #     logger.error(e)
        #     self.coll1.insert_one(info)


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


    def main(self):
        while True:
            try:
                res = self.local_VQ_conn.lpop("detailCookie")
                if res is None:
                    print(">>>>>>>>>>>>>>获取cookie信息..........")
                    time.sleep(0.5)
                else:
                    self.Reqest = json.loads(res.decode("utf-8"))
                    print(self.Reqest)
                    self.session.cookies = requests.utils.cookiejar_from_dict(self.Reqest["cookie_dict"])
                    _=1
                    with ThreadPoolExecutor(max_workers=3) as f:
                        futures=[]
                        while True:
                            res=self.local_conn.lpop("qinghai:company_id_01")
                            if res is None:
                                time.sleep(0.5)
                            else:
                                self.local_conn.lpush("qinghai:company_id_02", res)
                                self.local_conn.lpush("qinghai:company_id_03", res)
                                self.local_conn.lpush("qinghai:company_id_04", res)
                                info=json.loads(res.decode("utf-8"))
                                if "_id" in info:
                                    del info['_id']
                                print(info)
                                if self.local_conn.sadd("qinghai:filter:company", info["company"]):
                                    # res=f.submit(self.get_data, info=info)
                                    # futures.append(res)
                                    self.get_data(info)
                                else:
                                    logger.warning(f"【*】公司存在已过滤:{info}")
                                logger.info("。。。。。。。。。。。。。。第{}家数据".format(_))
                                _ += 1
                                # if len(futures) >= 100:
                                #     for future in futures:
                                #         future.result()
                                #     futures.clear()
            except Exception as e:
                logger.error(e)


if __name__ == '__main__':
    ll = Login_module()
    ll.main()

