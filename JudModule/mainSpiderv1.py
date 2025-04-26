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

from concurrent.futures import ThreadPoolExecutor
import execjs
import pika
from pymongo import MongoClient, WriteConcern
from lxml import etree
from retrying import retry
from ParseFile.parsehtml import parasHTML
import json
import time
import redis
import requests
from loguru import logger
from datetime import datetime
from reviewBUG.passCapTest.passVerity import Demo
from autoPass import main

class Login_module:

    def __init__(self):
        self.session = requests.session()
        self.client = MongoClient(host='192.168.5.167', port=27017)
        self.client_01 = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",
                                     authSource="admin")
        self.local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=1170)
        self.local_VQ_conn = redis.Redis(host='192.168.5.181', port=7933, db=0, password="fer@nhaweif576KUG",
                                         socket_connect_timeout=1170)
        self.local_40_conn = redis.Redis(host='192.168.5.199', port=8490, db=0, password="#Tn=EP(q%{",
                                         socket_connect_timeout=1170)
        self.coll_2 = self.client_01["company"]["guangdong"]["company"]
        self.coll = self.client["guangdong"]["company"]
        self.coll_1 = self.client["guangdong"]["company_with"]
        self.coli = self.client["guangdong"]["company_id"]
        self.collection_2 = self.client["guangdong"]["company_qualification"]
        self.collection_3 = self.client["guangdong"]["fail_company"]
        self.collection_4 = self.client["guangdong"]["fail_company_with"]
        self.collection_5 = self.client["guangdong"]["fail_qualification"]
        self.collection_6 = self.client["guangdong"]["fail_company_id"]
        self.coll1 = self.client["guangdong"]["公司详情失败公司id"]
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
        # resp = requests.get("https://myip.ipip.net", proxies=proxies)
        # if resp.status_code == 200:
        return proxies
        # else:
        #     raise Exception("请求代理")


    @retry(wait_fixed=1)
    def get_data(self, info):
        # try:
            headers = {
                "Host": "www.tianyancha.com",
                "Cache-Control": "max-age=0",
                "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Referer": "https://www.tianyancha.com/company/%s" % info["id"],
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            cookies = {
                "auth_token": self.Reqest["token"],
                "CUID": self.Reqest["cookie_dict"]["CUID"],
                "TYCID": self.Reqest["cookie_dict"]["TYCID"],
                "HWWAFSESID": self.Reqest["cookie_dict"]["HWWAFSESID"],
                "HWWAFSESTIME": self.Reqest["cookie_dict"]["HWWAFSESTIME"],
                "csrfToken": self.Reqest["cookie_dict"]["csrfToken"],
                "sajssdk_2015_cross_new_user": "1",
                "Hm_lvt_e92c8d65d92d534b0fc290df538b4758": "{},{}".format(
                    self.Reqest["cookie_dict"]["Hm_lvt_e92c8d65d92d534b0fc290df538b4758"], str(int(time.time()))),
                "HMACCOUNT": self.Reqest["cookie_dict"]["HMACCOUNT"],
                "bannerFlag": "true",
                "sensorsdata2015jssdkcross": self.Reqest["cookie_dict"]["sensorsdata2015jssdkcross"],
                "tyc-user-info": self.Reqest["cookie_dict"]["tyc-user-info"],
                "tyc-user-info-save-time": self.Reqest["cookie_dict"]["tyc-user-info-save-time"],
                "searchSessionId": self.Reqest["sessionNo"],
                # "Hm_lpvt_e92c8d65d92d534b0fc290df538b4758": str(int(time.time()) - 4000)
                "Hm_lpvt_e92c8d65d92d534b0fc290df538b4758": str(int(time.time()))
            }
            url = "https://www.tianyancha.com/company/%s" % str(info["id"])
            response = requests.get(url, headers=headers, cookies=cookies, proxies=self.proxy_list())
            logger.info(url)
            logger.info(self.Reqest["mobil"])
            logger.info(info)
            logger.info(response.status_code)
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
                    self.coll_1.with_options(write_concern=self.write_concern).insert_one({
                        'keys': data1})
                    self.coll.with_options(write_concern=self.write_concern).insert_one({
                        'keys': data2})
                    self.local_40_conn.sadd("guangdong:filter:company",item_info["company_name"])
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
                    self.local_40_conn.sadd("guangdong:filter:company", data["name"])
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
                    if "types" in data:
                        item_info["type"]=data["type"] if data["type"] else None
                    else:
                        item_info["type"]=None
                    # nameLevel3=industryInfo["nameLevel3"]
                    # 注册地址
                    if "regInstitute" in data:
                        item_info["registration_authority"] = data["regInstitute"] if data["regInstitute"] else None
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
                        "oldCompanyNameList": item_info["historyNames"]
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
                else:
                    # print("1111111>>>>>>>>>>>>",response.text)
                    print("1111111>>>>>>>>>>>>")
                    while True:
                        res = self.local_VQ_conn.lpop("detailCookie")
                        if res is None:
                            time.sleep(2)
                        else:
                            self.Reqest = json.loads(res.decode("utf-8"))
                            print(self.Reqest)
                            # self.session.cookies = requests.utils.cookiejar_from_dict(self.Reqest["cookie_dict"])
                            raise Exception("失效")
            elif response.status_code == 429:
                # print(response.text)
                # self.Reqest["headers"]=headers
                # self.Reqest["cookies"]=cookies
                # html = etree.HTML(response.text)
                # script = html.xpath("//body//script[1]/text()")[0]
                # jscode = open("2.js", encoding="utf-8").read()
                # span_par = execjs.compile(jscode).call("cc", script)
                # logger.info(span_par)
                # # raise Exception
                # _isPass = Demo(self.Reqest).passVerity(span_par)
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
                while True:
                    res = self.local_VQ_conn.lpop("detailCookie")
                    if res is None:
                        time.sleep(2)
                    else:
                        self.Reqest = json.loads(res.decode("utf-8"))
                        print(self.Reqest)
                        self.session.cookies = requests.utils.cookiejar_from_dict(self.Reqest["cookie_dict"])
                        raise Exception("失效")
        # except Exception as e:
        #     logger.error(e)
        #     if "_id" in info:
        #         del info["_id"]
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
            # try:
                res = self.local_VQ_conn.lpop("detailCookie")
                if res is None:
                    print(">>>>>>>>>>>>>>获取cookie信息..........")
                    time.sleep(0.5)
                else:
                    self.Reqest = json.loads(res.decode("utf-8"))
                    # self.Reqest = {"cookie_dict": {"Hm_lpvt_e92c8d65d92d534b0fc290df538b4758": "1730354414", "Hm_lvt_e92c8d65d92d534b0fc290df538b4758": "1730299193,1730304991,1730315249,1730321964", "sensorsdata2015jssdkcross": "%7B%22distinct_id%22%3A%20%22286973586%22%2C%20%22first_id%22%3A%20%22192e1290343183-0777bf62ad79da8-26001a51-1049088-192e129034572a%22%2C%20%22props%22%3A%20%7B%7D%2C%20%22identities%22%3A%20%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkyZTEyOTAzNDMxODMtMDc3N2JmNjJhZDc5ZGE4LTI2MDAxYTUxLTEwNDkwODgtMTkyZTEyOTAzNDU3MmEiLCIkaWRlbnRpdHlfbG9naW5faWQiOiIyODY5NzM1ODYifQ%3D%3D%22%2C%20%22history_login_id%22%3A%20%7B%22name%22%3A%20%22%24identity_login_id%22%2C%20%22value%22%3A%20%22286973586%22%7D%2C%20%22%24device_id%22%3A%20%22192e1290343183-0777bf62ad79da8-26001a51-1049088-192e129034572a%22%7D", "tyc-user-info": "%7B%22state%22%3A%20%224%22%2C%20%22vipManager%22%3A%20%220%22%2C%20%22mobile%22%3A%20%2217502039943%22%2C%20%22userId%22%3A%20%22286973586%22%2C%20%22isExpired%22%3A%20%220%22%7D", "tyc-user-info-save-time": "1730354414411", "tyc-user-phone": "%255B%252218587162714%2522%255D", "CUID": "401b8776e235253e172b5ad7f044821a", "TYCID": "60ffd670974d11efb3688307244048c3", "captcha_v4_user": "5baf8382e4f841549ece2127483c7392", "HWWAFSESID": "d30a414889af48bd00c", "HWWAFSESTIME": "1730354402843", "csrfToken": "hyPimxyb-GzC4loHtCE7yrdS"}, "ua": "Mozilla/5.0 (Windows; U; Windows NT 6.0; tr-TR) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5", "token": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNzUwMjAzOTk0MyIsImlhdCI6MTczMDM1NDQxMiwiZXhwIjoxNzMyOTQ2NDEyfQ.0boaqi_HocQ9qey8ntsdjyJITOSmAXMeeuHiS58n76C7u2vZrJAZFIMWbwELixxxINXgFBYOfsLkddveE5r9Kg", "sign": "7af7d7eb87a1c0866a5836fd93930439", "userid": "286973586", "sessionNo": "1730354414.41175842", "mobil": {"mobil": "17502039943", "pwd": "cc123456", "keys": "LoginUser"}}
                    print(self.Reqest)
                    # self.session.cookies = requests.utils.cookiejar_from_dict(self.Reqest["cookie_dict"])
                    _=1
                    with ThreadPoolExecutor(max_workers=3) as f:
                        futures=[]
                        while True:
                            res=self.local_40_conn.lpop("guangdong:company_id")
                            if res is None:
                                time.sleep(0.5)
                            else:
                                self.local_40_conn.lpush("guangdong:company_id_01", res)
                                self.local_40_conn.lpush("guangdong:company_id_02", res)
                                self.local_40_conn.lpush("guangdong:company_id_03", res)
                                self.local_40_conn.lpush("guangdong:company_id_04", res)
                                info=json.loads(res.decode("utf-8"))
                                if "_id" in info:
                                    del info['_id']
                                print(info)
                                if self.local_40_conn.sadd("guangdong:filter:company", info["company"]):
                                    # res=f.submit(self.get_data, info=info)
                                    # futures.append(res)
                                    self.get_data(info)
                                else:
                                    logger.warning(f"【*】公司存在已过滤:{info}")
                                logger.info("。。。。。。。。。。。。。。第{}家数据".format(_))
                                # self.conn.set("A12_detail_num", _)
                                _ += 1
                                # if len(futures) >= 3:
                                #     for future in futures:
                                #         future.result()
                                #     futures.clear()
            # except Exception as e:
            #     logger.error(e)


if __name__ == '__main__':
    ll = Login_module()
    ll.main()

