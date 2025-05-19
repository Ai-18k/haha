import ctypes
import json
import os
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import pika
import pymongo
from bson import ObjectId
from loguru import logger
from pymongo import errors, WriteConcern, MongoClient
from pymongo.errors import ConnectionFailure
from redis import Redis
from ParseFile.detailparam import getdata
from MQitems.PikaUse import SendMQ


# 加载静态配置
with open('Vchongqing.json', 'r', encoding='utf-8') as file:
    Vqtext = json.load(file)

class Merge:

    def __init__(self, key1):
        self.key1=key1
        self.serv_conn = Redis('139.9.70.234', 6379, 2, "anbo123", socket_connect_timeout=170)
        self.addr = json.loads(self.serv_conn.get(key1).decode('utf-8'))
        self.client = MongoClient(host='192.168.5.167', port=27017)
        self.local_conn = Redis("192.168.5." + self.addr[0], self.addr[1], self.addr[2], self.addr[3],socket_connect_timeout=1170)
        self.write_concern = WriteConcern(w=1)
        self.coll = self.client[key1]["sorcomp"]
        self.coll2 = self.client[key1]["MQfail"]
        self.coll4 = self.client[key1]["error_data"]
        self.coll4.create_index([('error_data', pymongo.ASCENDING)], unique=True, sparse=True)
        self.processed_ids = set()  # 处理过的公司ID集合
        self.thread_local = threading.local()

    def is_admin(self):
        try:
            return (sys.platform == "win32" and ctypes.windll.shell32.IsUserAnAdmin() != 0)
        except:
            return False

    def is_mongo_running(self):
        try:
            # 发送 ping 命令来测试连接
            self.client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False

    def run_as_admin(self, command):
        while True:
            if self.is_mongo_running():
                print("MongoDB 服务已启动")
                return True
            else:
                if self.is_admin():
                    subprocess.run(f"net start {command}", shell=True)
                    print(f"服务 {command} 已启动")
                else:
                    # 请求提升权限
                    try:
                        subprocess.run(
                            f'powershell -Command "Start-Process cmd.exe -ArgumentList \'/c net start {command}\' -Credential (New-Object System.Management.Automation.PSCredential(\'anbo\', (ConvertTo-SecureString \'anbo1234\' -AsPlainText -Force)))"',
                            shell=True)
                        print(f"服务 {command} 已启动")
                    except Exception as e:
                        print(f"启动服务失败: {e}")

    def senddata(self):
        try:
            SendMQ().mongoToMQ(2, self.thread_local.kechuang_item)
            self.thread_local.kechuang_item.clear()

            # if len(self.thread_local.data1_item) >= 20:
            SendMQ().mongoToMQ(1, self.thread_local.data1_item)
            self.thread_local.data1_item.clear()

            # if len(self.thread_local.data_item) >= 20:
            SendMQ().mongoToMQ(0, self.thread_local.data_item)
            self.thread_local.data_item.clear()
        except Exception as e:
            logger.error(e)

    def process_item_info(self, items):
        """处理每个公司信息"""
        for info in items:
            try:
                item_info = getdata(info)
                if "areaCode" not in info:
                    if info["name"] in Vqtext:
                        data1 = Vqtext[info["name"]]
                        item_info["city"] = data1["city"]
                        item_info["areaCode"] = data1["areaCode"]
                    else:
                        item_info["city"] = info.get("districtName", None)
                        item_info["areaCode"] = None
                else:
                    item_info["areaCode"] = info["areaCode"]
                    item_info["city"] = info["city"]
                if "_id" in item_info:
                    del item_info["_id"]
                # Ensure we don't process the same company twice
                company_id = item_info.get("tyxydm")  # Assuming tyxydm is unique
                if company_id in self.processed_ids:
                    logger.info(f"跳过重复公司: {company_id}")
                    return  # Skip processing if already processed

                # Mark as processed
                self.processed_ids.add(company_id)

                # Thread-local storage for data
                if not hasattr(self.thread_local, 'kechuang_item'):
                    self.thread_local.kechuang_item = []
                if not hasattr(self.thread_local, 'data_item'):
                    self.thread_local.data_item = []
                if not hasattr(self.thread_local, 'data1_item'):
                    self.thread_local.data1_item = []

                self.thread_local.data1_item.append(item_info["nameLevels"])
                self.thread_local.kechuang_item.extend(item_info['labelLists'])
                self.thread_local.data_item.append({
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
                "shzzlx": item_info["type"],
                "nsrsbh": item_info["nsrsbh"],
                "zzjgdm": item_info["zzjgdm"],
                "yyqx": item_info["yyqx"],
                "companyType": item_info["company_type"],
                "registrationAuthority": item_info["registration_authority"],
                "gszch": item_info["gszch"],
                "nsrzz": item_info["nsrzz"],
                "oldCompanyNameList": item_info["historyNames"],
                "city": item_info["city"],
                "areaCode": item_info["areaCode"],
                "dataSource": 1
            })
            except Exception as e:
                logger.error(f"处理失败: {e}")
                try:
                    self.coll4.insert_one(info)
                    print("数据插入成功！")
                except errors.DuplicateKeyError:
                    print("数据已存在，插入失败！")
        # 批量发送数据
            if len(self.thread_local.kechuang_item) >= 20:
               self.senddata()
        self.senddata()

    def copy_collection(self, db_name):
        try:
            old_db = self.client[db_name]
            old_collection = old_db["sorcomp"]
            last_id =ObjectId(self.serv_conn.get("copyDate:lasted").decode("utf-8")) if self.serv_conn.get("copyDate:lasted") else None
            currentPage = int(self.serv_conn.get("copyDate:pageNum").decode("utf-8")) if self.serv_conn.get("copyDate:pageNum") else 0
            pageSize = 1000
            total_copied = int(self.serv_conn.get("copyDate:total_copied").decode("utf-8")) if self.serv_conn.get("copyDate:total_copied") else 0
            with ThreadPoolExecutor(6) as workers:
                futures=[]
                while True:
                    query = {}
                    if last_id:
                        query["_id"] = {"$gt": last_id}  # 基于 _id 分页
                    docs_cursor = old_collection.find(query).sort("_id", 1).limit(pageSize)
                    docs = list(docs_cursor)
                    if not docs:  # 如果没有数据，退出循环
                        print(f"{db_name}.sorcomp 没有更多数据需要复制。")
                        break
                    futures.append(workers.submit(self.process_item_info, docs))
                    total_copied += len(docs)
                    self.serv_conn.set("copyDate:total_copied", total_copied)
                    # 打印进度
                    print(f"成功上传 {(currentPage + 1) * pageSize} 条数据到 mq ")
                    last_id = docs[-1]["_id"]
                    self.serv_conn.set("copyDate:lasted",str(last_id))
                    currentPage += 1
                    self.serv_conn.set("copyDate:pageNum",currentPage)
                    if len(futures)>=20:
                        for future in futures:
                            future.result()
                for future in futures:
                    future.result()
                print(f"数据库 {db_name} 的集合 sorcomp 完成数据上传，成功上传 {total_copied} 条记录。")
        except Exception as e:
            logger.error(f"复制 {db_name}.sorcomp 时出现错误: {e}")
            # self.start_service_windows('MongoDB')
            self.run_as_admin('MongoDB')
            raise ConnectionFailure("链接成功")

    def copy_mongo_multithreaded(self):
            try:
                threads = []
                with ThreadPoolExecutor(max_workers=6) as f:
                    threads.append(f.submit(self.copy_collection, db_name=self.key1))
                    # 等待所有线程完成
                    for future in as_completed(threads):
                        future.result()  # 这会确保所有线程都已经完成
            except ConnectionFailure:
                print("无法连接到 MongoDB 服务器。请检查网络连接。")
                # self.start_service_windows('MongoDB')
                # raise ConnectionFailure("链接成功")
            except Exception as e:
                print(f"出现错误: {e}")
                # self.start_service_windows('MongoDB')
                # raise ConnectionFailure("链接成功")


if __name__ == '__main__':
    serv_conn = Redis('139.9.70.234', 6379, 2, "anbo123", socket_connect_timeout=170)
    area_list = [
        # "tianjin","heilongjiang", "henan", "liaoning","shanxi","beijing","gansu","qinghai", "ningxia","sanxi","tianjin", "hebei",
        # "hainan","fujian","shanghai", "shandong","sichuan",
        "yunnan","xizang","anhui","jilin","guangxi", "neimenggu",
        "xinjiang", "guizhou", "chongqing", "hunan", "jiangxi", "guangdong",
        "hubei","jiangsu","zhejiang"
    ]
    for area in area_list:
        serv_conn.set("copyDate:area", area)
        area=serv_conn.get("copyDate:area").decode("utf-8") if serv_conn.get("copyDate:area") else "tianjin"
        Merge(area).copy_mongo_multithreaded()
        serv_conn.set("copyDate:lasted", "")
        serv_conn.set("copyDate:total_copied", 0)
        serv_conn.set("copyDate:pageNum",0)


