
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
import requests
import json
from loguru import logger
import time
import re
import redis
from pymongo import MongoClient
from retrying import retry
from RiskcontrolPass.passSpan import Test


"""
# server mongod 同  local mongod
福建数据-------> fujian.company
福建司法数据-------> fujian.company
福建专利数据-------> fujian.company
福建异常参数数据-------> fujian.fail.params
福建异常公司id数据-------> fujian.fail.companyid
福建MQ传送异常数据-------> fujian.fail.MQ_{company}
福建保存异常数据-------> fujian.fail.companyid

server mongod 同  local mongod
浙江数据-------> zhejiang.company
浙江司法数据-------> zhejiang.company
浙江专利数据-------> zhejiang.company
浙江异常参数数据-------> zhejiang.fail.params
浙江异常公司id数据-------> zhejiang.fail.companyid

"""

class SuccessCODE():
    """
    self.p_str 设置 "params:{00_05}" 00_05  06_10  11_15  16_18  21_24
    self.area  设置区域 fujian  zhejiang
    self.filter   设置过滤表  总表


    """
    def __init__(self):
        self.client = MongoClient(host='192.168.5.167', port=27017)
        self.client_01 = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",
                                     authSource="admin")
        self.conn = redis.Redis(host='182.43.38.79', port=6379, db=5, password="lzh990130", socket_connect_timeout=70)
        self.local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=70)
        # self.coll = self.client["fujian"]["company_id"]
        # self.coll_1 = self.client["fujian"]["company_id"]
        self.coll = self.client["zhejiang"]["company_id"]
        self.coll_1 = self.client["zhejiang"]["company_id"]
        self.coll2 = self.client["zhejiang"]["fail_地区时间参数"]
        self.session = requests.session()
        self.tag = {}
        self.Request = {}
        self.p_str = "11_15"
        self.area = "zhejiang"
        self.filter = "filter:zhejiang:company_id"

    @retry(wait_fixed=1000)
    def next_page(self, info):
        # try:
            page = 1
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
                    "cacheCode": info['areaCode'],
                    "sessionNo": self.Request["sessionNo"],
                    "customAreaCode": info['areaCode'],
                    "estiblishTimeStart": str(info["new_day"]),
                    "estiblishTimeEnd": str(info["next_day"]),
                    "pageNum": page
                }
                str_data = json.dumps(data, separators=(',', ':'))
                response = self.session.post(url, headers=headers, params=params, data=str_data)
                logger.info(self.Request["mobil"])
                logger.info(info)
                logger.info(response.status_code)
                print(response.json())
                if response.status_code == 200:
                    if response.json()["errorCode"] == "":
                            num = math.ceil(response.json()["data"]["companyTotal"] / 20) if response.json()["data"][
                                "companyTotal"] else 0
                            logger.info(f'这个链接共{num}页数据')
                            logger.info(f'当前是第{page}页')
                            if page > num:
                                return
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
                                    logger.success(info)
                                    self.conn.lpush(f"{self.area}:{self.p_str}:company_id", json.dumps(info))
                                else:
                                    logger.warning("【*】已过滤:{}".format({"company": item["name"], "id": item["id"]}))
                    else:
                        self.conn.rpush(f"params:{self.p_str}",json.dumps(info))
                        self.main()
                elif response.status_code ==429:
                    refer = re.findall("访问网址：(.*?)</li>", response.text, re.S)[0]
                    t_is = Test(response.text, self.session).validate_jy(refer)
                    if t_is:
                        logger.success("状态刷新成功！！恢复采集....")
                        raise Exception("状态刷新")
                else:
                    self.conn.rpush(f"params:{self.p_str}", json.dumps(info))
                    self.main()
                page += 1
        # except Exception as e:
        #         logger.error("数据:{} 报错：{}".format(info, e))
        #         self.coll2.insert_one(info)

    def main(self):
        while True:
            res = self.conn.lpop("testCookie")
            if res is None:
                time.sleep(0.5)
            else:
                self.Request = json.loads(res.decode("utf-8"))
                print(self.Request)
                self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                _ = 1
                comset = set()
                # with ThreadPoolExecutor(3) as f:
                while True:
                    res = self.conn.lpop(f"params:{self.p_str}")
                    if res is None:
                        logger.success("已全部采集完成！！")
                    info = json.loads(res.decode("utf-8"))
                    if "_id" in info:
                        del info["_id"]
                    if "company" not in info:
                        info_str = ",".join([str(info[i]) for i in info.keys()])
                        if info_str not in comset:
                            # f.submit(self.next_page,info=info)
                            print(info)
                            self.next_page(info)
                            # time.sleep(1.txt)
                        else:
                            logger.warning(f"【*】参数已经存在:{info}")
                        comset.add(info_str)
                        if len(comset) > 10000:
                            comset.clear()
                    else:
                        logger.warning("存在company_id")
                        self.conn.lpush("参数过滤", json.dumps(info))
                    _ += 1


if __name__ == '__main__':
    sc = SuccessCODE()
    sc.main()
