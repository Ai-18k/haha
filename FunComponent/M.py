#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :M.py
# @Time      :2024/11/22 12:56
# @Author    : 18k
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)
# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)

"""遍历表的字段"""
import threading
from concurrent.futures import ThreadPoolExecutor
from pymongo import MongoClient
from ParseFile.detailparam import getdata
from MQitems.PikaUse import SendMQ
from loguru import logger
from queue import Queue

# serv_client = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",authSource="admin")
serv_client = MongoClient(host='192.168.5.167', port=27017)


# print(serv_client.list_database_names())

def filterkeys(db):
    s_dbs = serv_client[db].list_collection_names()
    print(s_dbs)
    for db2 in s_dbs:
        PolyWeightRemov(db,db2)

# 去重
def PolyWeightRemov(key1,key2):
    # Aggregation pipeline
    pipeline = [
        {
            '$group': {
                # Group by the 'company' field
                'duplicates': {'$addToSet': '$_id'},  # Collect all _id values into an array
                'count': {'$sum': 1}  # Count occurrences of each group
            }
        },
        {
            '$match': {
                'count': {'$gt': 1}  # Match groups with more than one occurrence (duplicates)
            }
        },
        {
            '$project': {
                'duplicates': {
                    '$slice': ['$duplicates', 1, {'$subtract': [{'$size': '$duplicates'}, 1]}]
                }
            }
        }
    ]
    cli = serv_client[key1][key2]
    if key2=="company_id":
        pipeline[0]['$group']['_id']={'company':'$company'}
    elif  key2=="zlxx":
        pipeline[0]['$group']['_id'] = {'relationCompanyName': '$relationCompanyName'}
        pipeline[0]['$group']['_id'] = {'propertyNum': '$propertyNum'}
    elif  key2=="被执行人":
        pipeline[0]['$group']['_id'] = {'relationCompanyName': '$relationCompanyName'}
        pipeline[0]['$group']['_id'] = {'judicialNumber': '$judicialNumber'}
    else:
        return
    # Execute the aggregation pipeline
    results = list(cli.aggregate(pipeline))
    # Remove the duplicates
    for doc in results:
        for duplicate_id in doc['duplicates']:
            cli.delete_one({'_id': duplicate_id})

    # Close the connection
    serv_client.close()


class CompanySend(object):
    def __init__(self):
        self.q_queue=Queue()

    def verifyID(self,db, info):
        item_info = getdata(info)
        if "city" and "areaCode" not in item_info:
            data1 = serv_client[db]["company_id"].find_one({"company": info["name"]})
            print("----------------> ", data1)
            if not data1:
                data1 = dict()
                item_info["city"] = db
                item_info["areaCode"] = None
            else:
                item_info["city"] = data1["city"] if "city" in data1 else None
                item_info["areaCode"] = data1["areaCode"] if "areaCode" in data1 else None
        logger.info(item_info)
        self.q_queue.put(item_info)

    def findDB(self,db):
        f_dbs = serv_client[db].list_collection_names()
        if "sorcomp" in f_dbs:
            sorcomps = serv_client[db]["sorcomp"]
            currentPage = 0
            pageSize = 1000
            futures = []
            while True:
                data = sorcomps.find({}, {"_id": False}).skip((currentPage) * pageSize).limit(pageSize)
                if not data:
                    break
                _ = 0
                for info in data:
                    self.verifyID(db, info)
                    _ += 1
                    logger.error("【*】采集 {} 数据库的 第 {} 页  {} 数据！！".format(db, currentPage, currentPage * 1000 + _))
                currentPage += 1

    def keysiter(self):
        Overkey = []
        databases = serv_client.list_database_names()
        for database in databases:
            if database not in ["CCDate", "CCDate_id", 'CheckGaps', 'TYCDate', 'admin', 'config', 'filter', 'local','property', 'sfaj', "judicial"]:
                for i in range(3):
                    # findDB(database)
                    data = threading.Thread(target=self.findDB, args={"database":database})
            else:
                continue
            Overkey.append(database)
        logger.error(Overkey)

    """
    t_list = []
    t_url = threading.Thread(target=self.get_url)
    t_list.append(t_url)
    for i in range(3):
        t_get = threading.Thread(target=self.get_data)
        t_list.append(t_get)
    for i in range(2):
        t_parse = threading.Thread(target=self.parse_data)
        t_list.append(t_parse)
    t_save = threading.Thread(target=self.save_data)
    t_list.append(t_save)
    for t in t_list:
        t.setDaemon(True)  # 设置子线程守护主线程    主线程结束    子线程强制结束
        t.start()
        # print(111)
    
    for q in [self.url_queue, self.res_queue, self.save_queue]:
        # 查看队列的计算是否为0  如果不为0就会阻塞代码
        q.join()
    """

    def sendMQ(self):
        data_item = list()
        data1_item = list()
        kechuang_item = list()
        while True:
            item_info = self.q_queue.get()
            logger.info(item_info)
            if "_id" in item_info:
                del item_info["_id"]
            data1_item.append(item_info["nameLevels"])
            for dd in item_info['labelLists']:
                kechuang_item.append(dd)
            data_item.append({
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
                # 20241029新添加"shzzlx"
                "shzzlx": item_info["type"],
                "nsrsbh": item_info["nsrsbh"],
                "zzjgdm": item_info["zzjgdm"],
                "yyqx": item_info["yyqx"],
                "companyType": item_info["company_type"],
                "registrationAuthority": item_info["registration_authority"],
                "gszch": item_info["gszch"],
                "nsrzz": item_info["nsrzz"],
                "oldCompanyNameList": item_info["historyNames"],
                "provincialScope": None,
                # "city": None,
                # "areaCode": None
                "city": item_info['city'],
                "areaCode": item_info['areaCode'],
                "dataSource": 1
            })
            if len(kechuang_item) >= 20:
                SendMQ().mongoToMQ(2, kechuang_item)
                kechuang_item.clear()
            if len(data1_item) >= 20:
                SendMQ().mongoToMQ(1, data1_item)
                data1_item.clear()
            if len(data_item) >= 20:
                SendMQ().mongoToMQ(0, data_item)
                data_item.clear()
            self.q_queue.task_done()


if __name__ == "__main__":
    # CompanySend().keysiter()
    filterkeys("fujian")
    run_code = 0
    pass
