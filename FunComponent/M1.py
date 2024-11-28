# _*_ coding:UTF-8 _*
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

def findDB(db):
    with ThreadPoolExecutor(4) as f:
        f_dbs = serv_client[db].list_collection_names()
        if "sorcomp" in f_dbs:
            sorcomps = serv_client[db]["sorcomp"]
            currentPage =82
            pageSize = 1000
            futures = []
            while True:
                data = sorcomps.find({}, {"_id": False}).skip((currentPage) * pageSize).limit(pageSize)
                if not data:
                    break
                _ = 0
                for info in data:
                    item_info = getdata(info)
                    if "city" and "areaCode" not in item_info:
                        data1 = serv_client[db]["company_id"].find_one({"company": info["name"]})
                        # print("----------------> ", data1)
                        if not data1:
                            data1 = dict()
                            item_info["city"] = db
                            item_info["areaCode"] = None
                        else:
                            item_info["city"] = data1["city"] if "city" in data1 else None
                            item_info["areaCode"] = data1["areaCode"] if "areaCode" in data1 else None
                    logger.info(item_info)
                    _ += 1
                    logger.success("-------------------> 已上传 {} ！！".format(currentPage * 1000 + _))
                    yield item_info
                    # break
                currentPage += 1
                # break
            logger.error("【*】采集 {} 数据库的 第 {} 页  {} 数据！！".format(db, currentPage, currentPage * 1000 + _))


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
    cli = serv_client["fujian"]["2nf_add_company_id"]
    # Aggregation pipeline
    pipeline = [
        {
            '$group': {
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
    # Execute the aggregation pipeline
    results = list(cli.aggregate(pipeline))

    # Remove the duplicates
    for doc in results:
        for duplicate_id in doc['duplicates']:
            cli.delete_one({'_id': duplicate_id})

    # Close the connection
    serv_client.close()


def keysiter():
    Overkey = []
    data_item = list()
    data1_item = list()
    kechuang_item = list()
    databases = serv_client.list_database_names()
    for database in databases:
        if database not in ["CCDate", "CCDate_id", 'CheckGaps', 'TYCDate', 'admin', 'config', 'filter', 'local','property', 'sfaj', "judicial","anhui"]:
            for item_info in findDB(database):
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

# 49237   北京肆海建设有限公司
# 50470   北京正诺原科技发展有限公司

keysiter()