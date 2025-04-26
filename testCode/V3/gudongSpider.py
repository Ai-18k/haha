import json
import random
import time
from concurrent.futures import ThreadPoolExecutor
from loguru import logger
from curl_cffi import requests
from PikaUse import mongoToMQ
from config import Config


class Gudong(Config):


    def __init__(self, area):
        super().__init__(area)
        self.session = requests.Session()
        self.headers = {
                   "Accept": "application/json, text/plain, */*",
                   "Content-Type": "application/json",
                   "version": "TYC-Web",
                   "eventId": "i246",
                   "pm": "451",
                   "spm": "i246",
                   "page_id": "SearchResult"
                }
        self.Reqest=dict()
        self.finger = random.choices(["chrome99", "chrome100", "chrome101", "chrome104", "chrome107",
                                      "chrome110", "chrome116", "chrome119", "chrome120", "edge99",
                                      "edge101", "safari15_3",
                                      "safari15_5", "safari17_0", "chrome99"])[0]
        # self.gd=self.client[area]["gudong"]
        # self.filter_key = area + ":filter:gudong"
        # self.filter_key1 = area + ":filter:gdcomp"
        # self.comp_key = area + ":gudongList"
        # self.write_concern = WriteConcern(w=1)

    #
    # def offset(self):
    #     current_time = time.time()
    #     integer_part = int(current_time)
    #     decimal_part = current_time - integer_part
    #     integer_part_ms = integer_part * 1000
    #     decimal_part_ms = int(round(decimal_part, 3) * 1000)
    #     random_offset = random.randint(0, decimal_part_ms)
    #     random_timestamp = integer_part_ms + random_offset
    #     return random_timestamp
    #
    # def pj(self,item):
    #     _t = self.offset()
    #     if "pid" in item:
    #         url = "https://cloud-gateway.tianyancha.com/tyc-enterprise-graph/ei/human/card"
    #         pid = item["pid"]
    #         return url,{
    #             "humanId": pid,
    #             "_": str(_t),
    #             "traceId": str(_t - 3)
    #         }
    #     elif "gid" in item:
    #         url = "https://cloud-gateway.tianyancha.com/tyc-enterprise-company-agg/ei/company/card"
    #         gid = item["gid"]
    #         return url,{
    #             "companyId": gid,
    #             "companyName": "x",
    #             "_": str(_t),
    #             "traceId": str(_t - 3)
    #         }
    #     else:
    #         print(item)
    #         return {}
    #
    # def _pin(self,datas):
    #     items=datas["holder"]["items"]
    #     for item in items:
    #         name = item["name"]
    #         url,params=self.pj(item)
    #         response = requests.get(url, headers=self.headers, params=params)
    #         print(name + "------------------",response.json()["data"])
    #         item["data"]=response.json()["data"] if response.json()["data"] else None
    #     print(datas)
    #     self.saveDate({"type":0,"data":datas})
    #
    # def allinfo(self,id):
    #     _t = self.offset()
    #     url = "https://cloud-gateway.tianyancha.com/cloud-company-background/company/enterpriseMapV2"
    #     params = {
    #         "gid": id,
    #         "code": "all",
    #         "offset": "1",
    #         "limit": "10",
    #         "_": str(_t),
    #         "traceId": str(_t - 3)
    #     }
    #     response = self.session.get(url, headers=self.headers, params=params)
    #     print(response.json())
    #     if response.json()["message"]=='must login':
    #         return 1,"must login"
    #     elif "items" in response.json()["data"]["holder"]:
    #         datas = response.json()["data"]
    #         return 2,datas
    #     else:
    #         return 3,response.json()
    #
    # def getkpa(self,datas):
    #     items = datas["holder"]["items"]
    #     for item in items:
    #         "1984012283"
    #         hgid = str(item['hgid'])
    #         "22822"
    #         cid = str(item["cid"])
    #         headers = {
    #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    #             "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
    #         }
    #         cookies = {
    #             "CUID": self.Request["cookie_dict"]["CUID"],
    #             "TYCID":self.Request["cookie_dict"]["TYCID"],
    #             "auth_token": self.Request["token"]
    #         }
    #         url = f"https://www.tianyancha.com/human/{hgid}-c{cid}"
    #         response = self.session.get(url, headers=headers, cookies=cookies,impersonate=self.finger)
    #         if response.status_code == 200:
    #             html = etree.HTML(response.text)
    #             try:
    #                 json_date = json.loads(html.xpath('//script[@id="__NEXT_DATA__"]/text()')[0])
    #                 try:
    #                     gudong = json_date["props"]["pageProps"]["dehydratedState"]["queries"][7]["state"]["data"]["data"]["holderList"]
    #                 except (KeyError, IndexError, TypeError):
    #                     gudong =None
    #                 try:
    #                     faren = json_date["props"]["pageProps"]["dehydratedState"]["queries"][7]["state"]["data"]["data"]["legalList"]
    #                 except (KeyError, IndexError, TypeError):
    #                     faren =None
    #                 self.saveDate({"type":1,"data":{"company":datas["company"],"gudong":gudong,"faren":faren}})
    #             except Exception as e:
    #                 print(e)
    #         elif response.status_code == 429:
    #             while True:
    #                 res = self.conn.lpop("searchCookie")
    #                 if res is None:
    #                     print(">>>>>>>>>>>>>>获取cookie信息..........")
    #                     time.sleep(0.5)
    #                 else:
    #                     self.Request = json.loads(res.decode("utf-8"))
    #                     print(self.Request)
    #                     import requests
    #                     self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
    #                     self.getkpa(datas)
    #                     break

    def saveDate(self,datas):
        if datas["type"]==1:
            try:
                self.kpa.with_options(write_concern=self.write_concern).insert_one(datas["data"])
                # self.local_conn.sadd(self.filter_key1, datas["data"]["company"])
                logger.success("【*{}】关键人关联保存成功！！".format(datas["data"]['company']))
            except Exception as e:
                print(e)
        elif datas["type"]==2:
            try:
                self.sif.with_options(write_concern=self.write_concern).insert_one(datas["data"])
                logger.success("【*】股东信息保存成功:{}!!".format(datas["data"]))
            except Exception as e:
                print(e)
        else:
            try:
                self.gd.with_options(write_concern=self.write_concern).insert_one(datas["data"])
                self.local_conn.sadd(self.filter_key1, datas["data"]["company"])
                logger.success("【*{}】股东信息保存成功！！".format(datas["data"]['company']))
            except Exception as e:
                print(e)

    def paramdata(self,content,info):
        datas = content["data"]["result"]
        print(datas)
        shareholderInfo = []
        for data in datas:
            item = dict()
            item["shareholderName"] = data['shareHolderName']
            item["shareholderRatio"] = data["percent"]
            item["avatarAddress"] = data["logo"]
            item["shareholderType"] = data["shareHolderTypeOnPage"]
            item["subscribedCapitalContribution"] = data["totalCapital"]
            item["dateSubscribedCapitalContribution"] = data["investmentStartTime"]
            item["dateInitialShareholding"] = data["investmentEndTime"] if data["investmentEndTime"] else data[
                "latestCapitalTime"]
            item["companyName"] = info["company"]
            item["uniqueCode"] = data["shareHolderNameId"]
            item["tyshxydm"] = info["creditCode"]
            shareholderInfo.append(item)
        print(shareholderInfo)
        return shareholderInfo,datas

    def upsession(self):
        while True:
            res = self.conn.lpop("searchCookie")
            if res is None:
                print(">>>>>>>>>>>>>>获取cookie信息..........")
                time.sleep(0.5)
            else:
                self.Request = json.loads(res.decode("utf-8"))
                print(self.Request)
                import requests
                self.session.cookies = requests.utils.cookiejar_from_dict(self.Request["cookie_dict"])
                self.headers["X-TYCID"] = self.Request["cookie_dict"]["TYCID"]
                self.headers["X-AUTH-TOKEN"] = self.Request["token"]
                break

    def sinfo(self,info):
        url = "https://capi.tianyancha.com/cloud-company-background/companyV2/dim/historyHolder"
        params = {
            "_": str(int(time.time()*1000)),
        }
        data = {
            "gid": info["id"],
            "pageSize": 50,
            "pageNum": 1,
            "historyType": 2,
            "benefitSharesType": 1,
            "_unUseParam": 1,
            "percentLevel": "-100",
            "keyword": ""
        }
        data = json.dumps(data, separators=(',', ':'))
        response = self.session.post(url, headers=self.headers, params=params, data=data)
        print("现在的股东数据展示---------》",response.json())
        if response.json()["state"]=="ok":
            data,data1=self.paramdata(response.json(),info)
            return data,data1
        else:
            self.upsession()
            self.sinfo(info)
            return None,None

    def hsif(self,info):
        url = "https://capi.tianyancha.com/cloud-company-background/companyV2/dim/holder/latest/announcement"
        params = {
            "_": str(int(time.time()*1000)),
        }
        data = {
            "gid": info["id"],
            "pageSize": 50,
            "pageNum": 1,
            "historyType": None,
            "benefitSharesType": 1,
            "_unUseParam": 0
        }
        data = json.dumps(data, separators=(',', ':'))
        response = self.session.post(url, headers=self.headers, params=params, data=data)
        print("历史数据展示---------》",response.json())
        if response.json()["state"] == "ok":
            data,data1=self.paramdata(response.json(),info)
            return data,data1
        else:
            self.upsession()
            self.hsif(info)
            return None,None


    def send_data(self,flg,item):
        print("记录打点:",len(self.gudong_item))
        if flg==7:
            self.gudong_item.append(item)
            if len(self.gudong_item) >=5:
                logger.info(self.gudong_item)
                mongoToMQ(flg, self.gudong_item)
                logger.success(f"【*】发送成功：{self.gudong_item}")
                self.gudong_item.clear()

    def extract_info(self, item):
        info = {}
        if "id" in item:
            info["id"] = item["id"]
        elif "gid" in item:
            info["id"] = item["gid"]
        else:
            return {}
        return info

    def copycomp(self,workers):
        num = self.db.estimated_document_count()
        print(f"找到: 【{num}】 个文档！！")

        def copy(items):
            for item in items:
                info = dict()
                info["company"] = item["name"]
                info["creditCode"] = item["creditCode"]
                if self.extract_info(item):
                    info.update(self.extract_info(item))
                    print(info)
                    if self.local_conn.sadd(self.gudong_filter_key, info["company"]):
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

    def runspider(self,info):
        item, item1 = self.sinfo(info)
        data, data1 = self.hsif(info)
        if item1 or data1:
            self.saveDate({"type": 2, "data": {"shareholderInfo": item1, "shareholderInfoHistory": data1}})
        if not data:
            data = []
        if not item:
            item = []
        self.send_data(7, {"shareholderInfo": item, "shareholderInfoHistory": data})

    def main(self):
        with ThreadPoolExecutor(4) as executor:
            if not self.local_conn.exists(self.comp_key):
                self.copycomp(executor)
            self.upsession()
            futures = []
            _ = 1
            while True:
                company=self.local_conn.lpop(self.comp_key)
                if company is None:
                    time.sleep(0.5)
                # for company in res:
                company=json.loads(company.decode("utf-8"))
                print(company)
                if not self.local_conn.sismember(self.filter_key1,company["company"]):
                    futures.append(executor.submit(self.runspider,company))
                    # self.runspider(company)
                    if len(futures) >= 20:
                        for future in futures:
                            future.result()
            for future in futures:
                future.result()


if __name__ == '__main__':
    with ThreadPoolExecutor(4) as f:
        area_list=[
                "tianjin","heilongjiang","henan","hainan",
            # "sichuan","yunnan",
            #     "xizang","gansu","qinghai","ningxia","sanxi","anhui",
            #     "jilin","liaoning","shanxi","beijing","guangxi","neimenggu",
            #     "tianjin","hebei","xinjiang","guizhou","chongqing","hunan","jiangxi","guangdong",
            #     "hubei","shandong","fujian","shanghai","jiangsu","zhejiang"
            ]
        futures=[]
        for area in area_list:
            futures.append(f.submit(Gudong(area).main))
        for future in futures:
            future.result()
    # Gudong("qinghai").main()

















