
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
import re
from concurrent.futures import ThreadPoolExecutor
import requests
import json
from loguru import logger
import time
import redis
from pymongo import MongoClient
from RiskcontrolPass.passSpan import Test


class SuccessCODE():

    def __init__(self):


        self.conn = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123",socket_connect_timeout=70)
        # self.client = MongoClient(host='192.168.5.167', port=27017)
        self.client = MongoClient(host='127.0.0.1.txt', port=27017)
        self.client_01 = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",
                                     authSource="admin")
        # self.local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",
        #                               socket_connect_timeout=70)

        self.local_conn = redis.Redis(host='127.0.0.1.txt', port=7980, db=0, password="qwe!@#SDF345788",
                                      socket_connect_timeout=70)
        """本地数据保存"""
        self.coll = self.client["shanghai"]["company_id"]
        """服务器原始数据保存"""
        self.coll_1 = self.client_01["shanghai"]["company_id"]
        """异常数据保存"""
        self.coll2 = self.client["shanghai"]["fail_地区时间参数"]
        self.session = requests.session()
        """用于缓存redis的登录cookie信息和token等信息"""
        self.Request={}
        """去重表"""
        self.filter="shanghai:filter:company_id"
        self.filter_params = "shanghai:filter:params"

        self.com_id = "shanghai:company_id"
        self.params = "shanghai:params"

    def next_page(self,info,page):
        while True:
            try:
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
                    "pageNum": page
                }
                str_data = json.dumps(data, separators=(',', ':'))
                response = self.session.post(url, headers=headers, params=params, data=str_data)
                logger.info(info)
                logger.info(self.Request["mobil"])
                logger.info(response.status_code)
                if response.status_code == 200:
                    if response.json()["errorCode"] == "":
                        if "data" in response.json():
                            num = math.ceil(response.json()["data"]["companyTotal"] / 20) if response.json()["data"][
                                "companyTotal"] else 0
                            logger.info(f'这个链接共{num}页数据')
                            logger.info(f'当前是第{page}页')
                            if page > num:
                                break
                            compList = response.json().get("data").get("companyList")
                            for item in compList:
                                res = self.local_conn.sadd(self.filter, item["name"])
                                if res:
                                    """将获取到的结果更新到参数中保存"""
                                    info.update({"company":item["name"],"id":item["id"]})
                                    self.coll.insert_one(info)
                                    if "_id" in info:
                                        del info["_id"]
                                    self.coll_1.insert_one(info)
                                    if "_id" in info:
                                        del info["_id"]
                                        """本地数据保存"""
                                    self.local_conn.lpush(self.com_id, json.dumps(info))
                                    logger.success(info)
                                else:
                                    logger.warning("【*】已过滤:{}".format({"company": item["name"], "id": item["id"]}))
                        else:
                            while True:
                                res = self.conn.lpop("searchCookie")
                                if res is None:
                                    time.sleep(0.5)
                                else:
                                    self.Request = json.loads(res.decode("utf-8"))
                                    print(self.Request)
                                    self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                                    self.next_page(info, page)
                                    break
                            break
                    else:
                        while True:
                            res = self.conn.lpop("searchCookie")
                            if res is None:
                                time.sleep(0.5)
                            else:
                                self.Request = json.loads(res.decode("utf-8"))
                                print(self.Request)
                                self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                                self.next_page(info, page)
                                break
                        break
                elif response.status_code == 429:
                    refer = re.findall("访问网址：(.*?)</li>", response.text, re.S)[0]
                    t_is = Test(response.text, self.session).validate_jy(refer)
                    if t_is:
                        logger.success("状态刷新成功！！恢复采集....")
                        self.next_page(info,page)
                        break
                elif response.status_code == 404:
                    logger.error(f"{info}:页面不存在!")
                else:
                    while True:
                        res = self.conn.lpop("searchCookie")
                        if res is None:
                            time.sleep(0.5)
                        else:
                            self.Request = json.loads(res.decode("utf-8"))
                            print(self.Request)
                            self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                            self.next_page(info,page)
                            break
                    break
                page+=1
            # except Exception as e:
            except Exception as e:
                logger.error(e)


    def main_id(self):
        while True:
            res = self.conn.lpop("searchCookie")
            if res is None:
                print(">>>>>>>>>> 正在获取cookie信息。。。。。。。")
                time.sleep(0.5)
            else:
                self.Request = json.loads(res.decode("utf-8"))
                print(self.Request)
                self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                _ = 1
                with ThreadPoolExecutor(max_workers=4) as f:
                    futures = []
                    while True:
                        res = self.local_conn.lpop(self.params)
                        if res is None:
                            logger.success("已全部采集完成！！")
                            break
                        else:
                            info = json.loads(res.decode("utf-8"))
                            info_str = ",".join([str(info[i]) for i in info.keys()])
                            if self.local_conn.sadd(self.filter_params, info_str):
                                # futures.append(f.submit(self.next_page, info=info,page=1.txt))
                                self.next_page(info,1)
                            else:
                                logger.warning(f"【*】参数已经存在:{info}")
                            if len(futures)>=20:
                                for future in futures:
                                    try:
                                        future.result()
                                    except Exception as e:
                                        logger.error(f"Future generated an exception: {e}")
                                futures.clear()
                    for future in futures:
                        try:
                            future.result()
                        except Exception as e:
                            logger.error(f"Future generated an exception: {e}")


if __name__ == '__main__':
    # res = conn.lpop("detailCookie")
    # if res is None:
    #     time.sleep(0.5)
    # else:
    #     Request = json.loads(res.decode("utf-8"))
    #     print(Request)
    #     sc = SuccessCODE(Request)
    #     sc.main_id({'areaCode': '00310109V2020', 'base': 'sh', 'briefName': '虹口', 'city': '上海市', 'name': '虹口区', 'new_date': '2024-06-30', 'new_day': 1719676800000, 'next_date': '2024-07-01', 'next_day': 1719763200000, 'province': '上海市'})
    SC=SuccessCODE()
    SC.main_id()
