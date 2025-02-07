# _*_ coding:UTF-8 _*
import json
import sys
import os

from redis import Redis

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

serv_conn = Redis(host='192.168.5.191', port=14117, db=0, password="fer@nhaweif576KUG",socket_connect_timeout=1170)

serv_client = MongoClient(host='192.168.5.167', port=27017,retryWrites=True)

with open('Vchongqing.json', 'r', encoding='utf-8') as file:
    text =file.read()
Vqtext=json.loads(text)
# print(serv_client.list_database_names())

def findDB(db):
    with ThreadPoolExecutor(4) as f:
        f_dbs = serv_client[db].list_collection_names()
        if "sorcomp" in f_dbs:
            sorcomps = serv_client[db]["sorcomp"]
            currentPage = int(serv_conn.get("upkey:9E").decode("utf-8"))
            pageSize = 100
            futures = []
            while True:
                data = sorcomps.find({}, {"_id": False}).skip(currentPage * pageSize).limit(pageSize)
                data_found = False
                _ = 0
                for info in data:
                    item_info = getdata(info)
                    if "areaCode" not in info:
                        if info["name"] in Vqtext:
                            data1 = Vqtext[info["name"]]
                            item_info["city"] = data1["city"]
                            item_info["areaCode"] = data1["areaCode"]
                        else:
                            item_info["city"] = info["districtName"] if "districtName" in info else None
                            item_info["areaCode"] = None
                    else:
                        item_info["areaCode"] = info["areaCode"]
                        item_info["city"] = info["city"]
                    # logger.info(item_info)
                    _ += 1
                    logger.success("-------------------> 已上传 {} ！！".format(currentPage * 100 + _))
                    data_found = True
                    yield item_info
                    # break
                if not data_found:
                    print("没有更多数据了，查询结束")
                    break
                else:
                    serv_conn.set("upkey:9E", currentPage)
                    currentPage += 1  # 增加当前页数，准备查询下一页

                # break
            logger.error("【*】采集 {} 数据库的 第 {} 页  {} 数据！！".format(db, currentPage, currentPage * 100 + _))


def filterkeys(keys):
    for db1 in keys:
        s_dbs = serv_client[db1].list_collection_names()
        for db2 in s_dbs:
            if db2 == "company_id":
                """ company_id 去重 """
                db = serv_client[db1][db2]
                # print(db.find_one())

            elif db2 == "电信许可":
                """ 电信许可 去重 """
                dx_db = serv_client[db1][db2]
                print(dx_db.find_one())

            elif db2 == "软著著作权":
                """ 软著著作权 去重 """
                rz_db = serv_client[db1][db2]
                print(rz_db.find_one())

# 去重
def PolyWeightRemov():
    cli = serv_client["yunnan"]["fail_电信许可"]
    pipeline = [
        {
            '$group': {
                # '_id': {'name': '$name'},  # Group by the 'company' field
                '_id': {'company': '$company'},  # Group by the 'company' field
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
    results = list(cli.aggregate(pipeline))

    for doc in results:
        for duplicate_id in doc['duplicates']:
            cli.delete_one({'_id': duplicate_id})

    serv_client.close()


# PolyWeightRemov()


def search(company):
    db=serv_client["beijing"]["sorcomp"]
    res=db.find({"company":company})
    print(res)

# search("北京汇远成才商贸有限公司")

def keysiter(KEY):
    Overkey = []
    data_item = list()
    data1_item = list()
    kechuang_item = list()
    databases = serv_client.list_database_names()
    for database in databases:
        # if database not in ["CCDate", "CCDate_id", 'CheckGaps', 'TYCDate', 'admin', 'config', 'filter', 'local','property', 'sfaj', "judicial","anhui"]:
        if  database==KEY:
            items=findDB(database)
            for item_info in items:
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
        else:
             continue
        Overkey.append(database)
    logger.error(Overkey)



keysiter("zhejiang")