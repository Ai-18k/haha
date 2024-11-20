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
from concurrent.futures import ThreadPoolExecutor
# from curl_cffi import requests
# import requests_html
import requests
import json
from loguru import logger
import time
import re
import redis
from pymongo import MongoClient
from retrying import retry
from RiskcontrolPass.passSpan import Test



class SuccessCODE():

    def __init__(self):
        self.conn = redis.Redis(host='182.43.38.79', port=6379, db=5, password="lzh990130", socket_connect_timeout=70)
        self.client = MongoClient(host='192.168.5.167', port=27017)
        self.client_01 = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",
                                     authSource="admin")
        self.local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",
                                      socket_connect_timeout=70)
        self.coll = self.client["fujian"]["company_id"]
        self.coll_1 = self.client_01["fujian"]["company_id"]
        self.session = requests.session()
        self.Request = {}
        self.p_str = "16_18"
        self.area = "fujian"
        self.filter = "全部companyID去重"
        self.page = 1

    @retry(wait_fixed=1000)
    def next_page(self, info):
        while True:
            url = "https://capi.tianyancha.com/cloud-tempest/web/searchCompanyV3"
            headers = {
                "Host": "capi.tianyancha.com",
                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                             "Chrome\";v=\"114\"",
                "sec-ch-ua-platform": "\"Windows\"",
                "X-TYCID": self.Request["sign"],
                "DNT": "1.txt",
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
                "pageNum": self.page
            }
            str_data = json.dumps(data, separators=(',', ':'))
            response = self.session.post(url, headers=headers, params=params, data=str_data)
            logger.info(info)
            logger.info(self.Request["mobil"])
            logger.info(response.status_code)
            print(response.json())
            if response.status_code == 200:
                if response.json()["errorCode"] == "":
                    if "data" in response.json():
                        num = math.ceil(response.json()["data"]["companyTotal"] / 20) if response.json()["data"][
                            "companyTotal"] else 0
                        logger.info(f'这个链接共{num}页数据')
                        logger.info(f'当前是第{self.page}页')
                        if self.page > num:
                            break
                        compList = response.json().get("data").get("companyList")
                        for item in compList:
                            res = self.local_conn.sadd(self.filter, item["name"])
                            if res:
                                info.update({"company": item["name"], "id": item["id"]})
                                self.coll.insert_one(info)
                                # if "_id" in info:
                                #     del info["_id"]
                                self.coll_1.insert_one(info)
                                # if "_id" in info:
                                #     del info["_id"]
                                self.conn.lpush(f"{self.area}:{self.p_str}:company_id", json.dumps(info))
                                logger.success(info)
                            else:
                                logger.warning("【*】已过滤:{}".format({"company": item["name"], "id": item["id"]}))
                    else:
                        res = self.conn.lpop("searchCookie")
                        if res is None:
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            raise Exception("失效")
                else:
                    res = self.conn.lpop("searchCookie")
                    if res is None:
                        time.sleep(0.5)
                    else:
                        self.Request = json.loads(res.decode("utf-8"))
                        print(self.Request)
                        self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                        raise Exception("失效")
            elif response.status_code == 429:
                refer = re.findall("访问网址：(.*?)</li>", response.text, re.S)[0]
                t_is = Test(response.text, self.session).validate_jy(refer)
                if t_is:
                    logger.success("状态刷新成功！！恢复采集....")
                    raise Exception("状态刷新")
            elif response.status_code == 404:
                logger.error(f"{info}:页面不存在!")
            else:
                res = self.conn.lpop("searchCookie")
                if res is None:
                    time.sleep(0.5)
                else:
                    self.Request = json.loads(res.decode("utf-8"))
                    print(self.Request)
                    self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                    raise Exception("失效")
            self.page += 1


    def main(self):
        while True:
            res = self.conn.lpop("searchCookie")
            if res is None:
                time.sleep(0.5)
            else:
                self.Request = json.loads(res.decode("utf-8"))
                print(self.Request)
                self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                _ = 1
                with ThreadPoolExecutor(4) as f:
                    while True:
                        res = self.conn.lpop(f"params:{self.p_str}")
                        if res is None:
                            logger.success("已全部采集完成！！")
                        info = json.loads(res.decode("utf-8"))
                        orgType = ["有限责任公司", "股份有限公司", "集体所有制", "股份合作制", "国有企业",
                                   "个人独资企业","有限合伙", "普通合伙", "外商投资企业", "港、澳、台", "联营企业", "私营企业"]
                        for name in orgType:
                            info["orgType"] = name
                            if "_id" in info:
                                del info["_id"]
                            if "company" not in info:
                                info_str = ",".join([str(info[i]) for i in info.keys()])
                                if self.local_conn.sadd("fujian:filter:params", info_str):
                                    self.page = 1
                                    # f.submit(self.next_page, info=info)
                                    self.next_page(info)
                                    # time.sleep(1.txt)
                                else:
                                    logger.warning(f"【*】参数已经存在:{info}")
                            else:
                                logger.warning("{}：存在company_id".format(info))
                                self.conn.lpush("参数过滤", json.dumps(info))
                        logger.info(f"。。。。。。。。。。。第{_}个数据")
                        _ += 1


if __name__ == '__main__':
    sc = SuccessCODE()
    sc.main()

    # print(json.loads(conn.lpop("params").decode("utf-8"))['cacheCode'])