import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
import loguru
from pymongo import MongoClient, WriteConcern
from redis import Redis
import requests
from retrying import retry
from tqdm import tqdm

from config import checkconfig


class Gudong:


    def __init__(self,area):
        self.config = checkconfig("bendi")
        self.session = requests.session()
        self.local_conn=Redis("192.168.5.180",14307,3,"fer@nhaweif576KUG",socket_connect_timeout=1155)
        self.local_VQ_conn =Redis("192.168.5.%s" % self.config["uAddr"][0],
                                         self.config["uAddr"][1],
                                         self.config["uAddr"][2],
                                         self.config["uAddr"][3],
                                         socket_connect_timeout=1155)
        self.client = MongoClient("192.168.5.167",27017)
        self.db=self.client[area]["sorcomp"]
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "version": "TYC-Web",
            "x-spm-referer": "https://graph.tianyancha.com/web/tree/enterprise_structure?cid=22822&category=companyStructure&depth=1&entityType=2&spm=&pm=&export=&canvasType=",
            "referrer_pm": "",
            "laneTag": "false",
            "Content-Type": "application/json"
        }
        self.gd=self.client[area]["gudong"]
        self.filter_key = area + ":filter:gudong"
        self.filter_key1 = area + ":filter:gdcomp"
        self.comp_key = area + ":gudongList"
        self.write_concern = WriteConcern(w=1)


    def offset(self):
        current_time = time.time()
        integer_part = int(current_time)
        decimal_part = current_time - integer_part
        integer_part_ms = integer_part * 1000
        decimal_part_ms = int(round(decimal_part, 3) * 1000)
        random_offset = random.randint(0, decimal_part_ms)
        random_timestamp = integer_part_ms + random_offset
        return random_timestamp


    def pj(self,item):
        _t = self.offset()
        if "pid" in item:
            url = "https://cloud-gateway.tianyancha.com/tyc-enterprise-graph/ei/human/card"
            pid = item["pid"]
            return url,{
                "humanId": pid,
                "_": str(_t),
                "traceId": str(_t - 3)
            }
        elif "gid" in item:
            url = "https://cloud-gateway.tianyancha.com/tyc-enterprise-company-agg/ei/company/card"
            gid = item["gid"]
            return url,{
                "companyId": gid,
                "companyName": "x",
                "_": str(_t),
                "traceId": str(_t - 3)
            }
        else:
            print(item)
            return {}

    def _pin(self,datas,company):
        items=datas["holder"]["items"]
        for item in items:
            name = item["name"]
            url,params=self.pj(item)
            response = requests.get(url, headers=self.headers, params=params)
            print(name + "------------------",response.json()["data"])
            item["data"]=response.json()["data"] if response.json()["data"] else None
        print(datas)
        self.saveDate(datas,company)

    def allinfo(self,id):
        _t = self.offset()
        url = "https://cloud-gateway.tianyancha.com/cloud-company-background/company/enterpriseMapV2"
        params = {
            "gid": id,
            "code": "all",
            "offset": "1",
            "limit": "10",
            "_": str(_t),
            "traceId": str(_t - 3)
        }
        response = self.session.get(url, headers=self.headers, params=params)
        print(response.json())
        if response.json()["message"]=='must login':
            return 1,"must login"
        elif "items" in response.json()["data"]["holder"]:
            datas = response.json()["data"]
            return 2,datas
        else:
            return 3,response.json()

    def saveDate(self,datas,company):
        if "_id" in datas:
            del datas["_id"]
        try:
            self.gd.with_options(write_concern=self.write_concern).insert_one(datas)
            self.local_conn.sadd(self.filter_key1, company["company"])
            logger.success(f"【*{company['company']}】股东信息保存成功！！")
        except Exception as e:
            print(e)


    def _pushcom(self,comp):
        self.local_conn.lpush(self.comp_key, comp.decode())

    def extract_info(self, item):
        info = {"company": item["name"]}
        if "id" in item:
            info["id"] = item["id"]
        elif "gid" in item:
            info["id"] = item["gid"]
        else:
            return None
        return info

    def copycomp(self,workers):
        num = self.db.estimated_document_count()
        print(f"找到: 【{num}】 个文档！！")

        def copy(items):
            for item in items:
                info = dict()
                info["company"] = item["name"]
                if self.extract_info(item):
                    info = self.extract_info(item)
                    print(info)
                    if self.local_conn.sadd(self.filter_key, info["company"]):
                        self.local_conn.lpush(self.comp_key , json.dumps(info))
                    else:
                        print(info["company"] + " :重复数据!!")
                else:
                    print(item)
                    del item["_id"]
                    with open("无id.json","a",encoding="utf-8")as file:
                        file.write(json.dumps(item))
                    continue

        # last_id =ObjectId("67489ff6779e716dade3fdd6")
        last_id = None
        currentPage = 0
        pageSize = 1000
        total_copied = 0
        futures = []
        while True:
            query = {}
            if last_id:
                query["_id"] = {"$gt": last_id}  # 基于 _id 分页
            docs_cursor = self.db.find(query).sort("_id", 1).limit(pageSize)
            docs = list(docs_cursor)
            if not docs:  # 如果没有数据，退出循环
                print("sorcomp 没有更多数据需要复制。")
                break
            futures.append(workers.submit(copy, docs))
            total_copied += len(docs)
            last_id = docs[-1]["_id"]
            currentPage += 1
            if len(futures) >= 20:
                for future in futures:
                    future.result()
        for future in futures:
            future.result()
        print("导入成功！！")
        print(f"数据库sorcomp 完成数据上传，成功上传 {total_copied} 条记录。")

    @retry(wait_fixed=1000)
    def main(self):
        with ThreadPoolExecutor(4) as executor:
            if not self.local_conn.exists(self.comp_key):
                self.copycomp(executor)
            while True:
                res = self.local_VQ_conn.lpop("searchCookie")
                if res is None:
                    print(">>>>>>>>>>>>>>获取cookie信息..........")
                    time.sleep(0.5)
                else:
                    Request = json.loads(res.decode("utf-8"))
                    print(Request)
                    self.session.cookies = requests.utils.cookiejar_from_dict(Request["cookie_dict"])
                    self.headers["X-TYCID"]=Request["cookie_dict"]["TYCID"]
                    self.headers["X-AUTH-TOKEN"]=Request["token"]
                    futures = []
                    _ = 1
                    while True:
                    # res = self.local_conn.lrange(self.comp_key,0,-1)
                        company=self.local_conn.lpop(self.comp_key)
                        if res is None:
                            time.sleep(0.5)
                        # for company in res:
                        company=json.loads(company.decode("utf-8"))
                        print(company)
                        if not self.local_conn.sismember(self.filter_key1,company["company"]):
                            id=company["id"]
                            flg,items=self.allinfo(id)
                            print("【" + str(flg) + str(items) + "】")
                            if flg==2:
                                # print(items)
                                futures.append(executor.submit(self._pin,items,company))
                                _+=1
                            elif flg==1:
                                self.local_conn.lpush(self.comp_key, json.dumps(company))
                                raise Exception("must login")
                            else:
                                self.local_conn.sadd(self.filter_key1, company["company"])
                                print(company["company"]+" :未找到相关信息！！")
                            if len(futures) >= 20:
                                for future in futures:
                                    future.result()
                    for future in futures:
                        future.result()


if __name__ == '__main__':
    Gudong("fujian").main()


















