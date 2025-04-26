# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@FileName：copyLocallToServer.py
@Description：
@Author：18k
@Time：2024/5/6 1:25
@Department：部门
@Website：站点
@Copyright：©2019-2024 职业
:return:
"""

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)
# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)


import json
import re
from concurrent.futures.thread import ThreadPoolExecutor
import pymysql
import redis
from loguru import logger
import pymongo
import random
import pika
import aiomysql
import asyncio
import datetime

client_01 = pymongo.MongoClient(host='139.9.70.234', port=12700, username="root",
                                password="QuyHlxXhW2PSHTwT",
                                authSource="admin")
coll_2 = client_01["backups"]["add_company_id"]
client = pymongo.MongoClient(host='192.168.5.167', port=27017)
collection = client["TYCDate"]["company"]
collection_2 = client["TYCDate"]["company_with"]
collection_2_1 = client["mydata"]["coll"]

conn = redis.Redis(host='182.43.38.79', port=6379, db=2, password="lzh990130", socket_connect_timeout=170)
local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@", socket_connect_timeout=170)
# conn_1 = redis.Redis(host='127.0.0.1',port=6379,db=5)
# db= pymysql.connect(host="192.168.5.53",
#                 port=3306,
#                 user="test",
#                 password="test",
#                 db="test_01")

# local_db= pymysql.connect(host="127.0.0.1",
#                 port=3306,
#                 user="root",
#                 password="root",
#                 db="test_01")
# local_cursor =local_db.cursor()
# serv_db = pymysql.connect(host="182.43.38.79",
#                 port=3306,
#                 user="qqbx",
#                 password="qqbx123",
#                 db="qqx_tender")
# serv_cursor =serv_db.cursor()

"""本地mongo"""
client_1 = pymongo.MongoClient(host='192.168.5.167', port=27017)
# 过滤
# collection_3=client_1["TYCDate"]["rocrd"]
#
# # 新建company表   company_with表
# """30"""
collection_5 = client_1["fujian"]["company"]
# collection_5_2=client_1["CCDate_id"]["company"]
#
# collection_5_4=client_1["CCDate"]["copy_company_qualification"]
#
# collection_5_3=client_1["fujian"]["company"]
#
# collection_5_1=client_1["filter"]["company"]
# collection_5_1.create_index([('company', pymongo.ASCENDING)], unique=True)
# """12"""
# collection_6=client_1["TYCDate"]["company_with"]
#
# collection_6_2=client_1["fujian"]["zlxx"]
#
collection_6_1 = client_1["filter"]["company_with"]
# collection_6_1.create_index([('company_with', pymongo.ASCENDING)], unique=True)
#
collection_7 = client_1["TYCDate"]["fail_company"]
collection_7_2 = client_1["TYCDate"]["fail_with_company"]
collection_7_3 = client_1["TYCDate"]["fail_qualification"]
collection_7_1 = client_1["fujian"]["fail_judicial_with"]
collection_8_1 = client_1["fujian"]["fail_property_with"]

collection_8 = client_1["CCDate"]["sfaj"]
collection_9 = client_1["CCDate"]["zlxx"]

"""将本地mysql的数据公司名导入mongo里面作为去重值"""


def cache_data():
    sql = "select * from company;"
    # sql = "select * from  company LIMIT 2625,329;"
    # serv_cursor.execute(sql)
    serv_cursor.execute(sql)
    data = serv_cursor.fetchall()
    print(len(data))
    unique_data = set()
    result = []
    for item in data:
        # print(item[2])
        if item[2] not in unique_data:
            result.append(item)
            unique_data.add(item[2])
    print(len(result))
    for original_tuple in result:
        # new_tuple = (0,) + original_tuple[1:]
        # print(new_tuple)
        try:
            try:
                data = original_tuple[17] if original_tuple[17] else None
                year = data.year if data else 0
                month = data.month if data else 0
                day = data.day if data else 0
                my_datetime = datetime.datetime(year, month, day)
                n_tuple = (0,) + original_tuple[1:17] + (my_datetime,) + original_tuple[18:]
                logger.info(f"mongo数据保存:{n_tuple}")
                collection_5_1.insert_one({'company': n_tuple[3]})

                print("数据插入成功！")
            except pymongo.errors.DuplicateKeyError:
                print("数据已存在，插入失败！")
        except:
            with open("a.json", "w") as f:
                f.write(str(original_tuple))
        break

        # conn.sadd("filter:compSet",str(new_tuple[2]))


# cache_data()


"""保存本地服务器mysql数据"""
def save_com_data(data):
    sql_code = "INSERT INTO company values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
               "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
               "%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        logger.info(data)
        serv_cursor.execute(sql_code, data)
        serv_db.commit()
        logger.success(f"company_data:{data}数据插入成功!!!")
    except Exception as e:
        logger.error(f"插入失败！！")
        serv_db.rollback()


"""本地mysql数据company_copy数据copy到company """
def localTOLocal_data():
    sql = "select * from company;"
    # sql = "select * from  company LIMIT 2625,329;"
    # serv_cursor.execute(sql)
    serv_cursor.execute(sql)
    data = serv_cursor.fetchall()
    print(len(data))
    unique_data = set()
    result = []
    for item in data:
        # print(item[2])
        if item[2] not in unique_data:
            result.append(item)
            unique_data.add(item[2])
    print(len(result))
    for original_tuple in result:
        try:
            new_tuple = (0,) + original_tuple[1:]
            company = original_tuple[3]
            res = conn.sadd("filter:compSet", company)
            print(original_tuple[3])
            try:
                collection_5_1.insert_one({'company': company})
                collection_5.insert_one({"data": new_tuple})
                print(new_tuple)
                print("数据插入成功！")
            except pymongo.errors.DuplicateKeyError:
                print("数据已存在，插入失败！")
            if res:
                n_tuple = (0,) + original_tuple[2:]
                logger.info(n_tuple)
                save_com_data(n_tuple)
            else:
                logger.error("数据重复！！")
        except:
            with open("date_error.json", "a", encoding="utf-8") as f:
                f.write(str(original_tuple))
        # break

# localTOLocal_data()


"""服务器company表数据保存  29"""
def Toservice_data(data):
    sql_code = "INSERT INTO company values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
               "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
               "%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        serv_cursor.execute(sql_code, data)
        serv_db.commit()
        logger.success(f"company_data:{data}数据插入成功!!!")
    except Exception as e:
        logger.error(f"【save_company_data】保存失败！！失败详情：{e}")
        logger.error(f"【save_company_data】插入失败！！数据源为：{data}")
        serv_db.rollback()


"""本地服务器company_copy数据查询，修改字段传到服务器"""
def cache_copy_data():
    new_list_01 = []
    sql = "select * from company_copy;"
    # sql = "select * from  company LIMIT 2625,329;"
    serv_cursor.execute(sql)
    data = serv_cursor.fetchall()
    print(len(data))
    unique_data = set()
    result = []
    for item in data:
        if item[3] not in unique_data:
            result.append(item)
            unique_data.add(item[3])
    print(len(result))
    for original_tuple in result:
        new_tuple = (0,) + original_tuple[2:]
        res = conn.sadd("filter:compSet", str(new_tuple[2]))
        if res:
            logger.info(new_tuple)
            # Toservice_data(new_tuple)
        else:
            logger.error(f"数据重复:{new_tuple}")
        break


# cache_copy_data()


"""本地mysql数据库去重"""
def send_local_data():
    sql = "select * from company;"
    # sql = "select company_name from  company LIMIT 0,1000;"
    serv_cursor.execute(sql)
    data = serv_cursor.fetchall()
    print(len(data))
    unique_data = set()
    result = []
    _ = 0
    for item in data:
        if item[2] not in unique_data:
            result.append(item)
            unique_data.add(item[2])
            _ += 1
    print(len(result))
    for original_tuple in result:
        try:
            new_tuple = (0,) + original_tuple[2:]
            company = original_tuple[3]
            res = conn.sadd("filter:serv_company", company)
            try:
                collection_5_1.insert_one({'company': company})
                collection_5.insert_one({"data": new_tuple})
                print("数据插入成功！")
            except pymongo.errors.DuplicateKeyError:
                print("数据已存在，插入失败！")
            if res:
                logger.info(new_tuple)
                # Toservice_data(new_tuple)
            else:
                logger.error(f"数据重复:{new_tuple}")
        except:
            print(original_tuple)
        break


# send_local_data()


"""读取mongo数据库数据 去掉company_id  保存到服务器"""
def save_industry_data(data):
    sql_code = "INSERT INTO company_industry_with_company() values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        logger.info(data)
        serv_cursor.execute(sql_code, data)
        serv_db.commit()
        logger.success(f"industry_data:{data}数据插入成功!!!")
    except Exception as e:
        logger.error(f"插入失败！！")
        serv_db.rollback()


def save_company_data(data):
    sql_code = "INSERT INTO company() values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
               "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
               "%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        logger.info(data)
        serv_cursor.execute(sql_code, data)
        serv_db.commit()
        logger.success(f"company_data:{data}数据插入成功!!!")
    except Exception as e:
        logger.error(f"插入失败！！")
        serv_db.rollback()


def localMongoToServ():
    # 台式机mongo
    # resules=list(collection.find())
    # 本机mongo 表一
    resules = list(collection.find())
    # 本机mongo 表二
    # resules=list(collection_2.find())
    for item in resules:
        data = tuple(item["data"])
        print(len(data))
        if len(data) < 20:  # 12
            # 服务器redis
            res = conn.sadd("filter:with_compSet", data[7])
            # 本地redis
            # res=conn.sadd("filter:with_compSet",data[7])
            try:
                collection_6_1.insert_one({'company_with': data[7]})
                collection_6.insert_one({
                    'company_with': data
                })
                print("数据插入成功！")
            except pymongo.errors.DuplicateKeyError:
                print("数据已存在，插入失败！")
            if res:
                logger.info(data)
                save_industry_data(data)
            else:
                logger.error(f"数据已经保存{data}")
        else:
            res = conn.sadd("filter:compSet", data[3])
            new_tuple = (0,) + data[1:]
            try:
                logger.info(f"mongo数据保存:{new_tuple}")
                collection_5_1.insert_one({'company': new_tuple[3]})
                collection_5.insert_one({
                    'company': new_tuple
                })
                print("数据插入成功！")
            except pymongo.errors.DuplicateKeyError:
                print("数据已存在，插入失败！")
            if res:  # 30
                n_tuple = (0,) + data[2:]
                save_company_data(n_tuple)
            else:
                logger.error(f"数据已经保存{data}")


# localMongoToServ()


"""本地mongo 数据copy到服务器mysql"""
def MongoToMong():
    # 台式机mongo
    # resules=list(collection.find())
    # 本机mongo
    # resules=list(collection_5.find())
    # resules_01=list(collection_6.find())
    # resules=list(collection_4.find())
    i = 1
    while True:
        for item in resules[i * 1000:(i + 1) * 1000]:
            data = tuple(item["data"])
            if data is None:
                break
            logger.info(data)
            break
            if len(data) == 12:  # 12
                res = conn.sadd("filters:compSet", data[7])
                try:
                    collection_1.insert_one({'keys': data[7]})
                    print("数据插入成功！")
                except pymongo.errors.DuplicateKeyError:
                    print("数据已存在，插入失败！")
                if res:
                    logger.info(data)
                    save_industry_data(data)
                    try:
                        collection_6_1.insert_one({'company_with': data[7]})
                        collection_6.insert_one({"data": data})
                        print("数据插入成功！")
                    except pymongo.errors.DuplicateKeyError:
                        print("数据已存在，插入失败！")
                else:
                    logger.error(f"数据已经保存{data}")
            elif len(data) == 30:
                res = conn.sadd("filter:with_compSet", data[3])
                try:
                    collection_1.insert_one({'keys': data[3]})
                    print("数据插入成功！")
                except pymongo.errors.DuplicateKeyError:
                    print("数据已存在，插入失败！")
                new_tuple = (0,) + data[2:]
                if res:  # 30
                    logger.info(new_tuple)
                    save_company_data(new_tuple)
                try:
                    collection_5_1.insert_one({'company': data[3]})
                    collection_5.insert_one({"data": new_tuple})
                    print("数据插入成功！")
                except pymongo.errors.DuplicateKeyError:
                    print("数据已存在，插入失败！")

                else:
                    logger.error(f"数据已经保存{data}")
            else:
                logger.error(data)
            resules.append()


# MongoToMong()


"""mysql数据库传mysql数据库"""
def save_company_copy(data):
    sql_code = "INSERT INTO company() values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
               "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
               "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        logger.info(data)
        serv_cursor.execute(sql_code, data)
        serv_db.commit()
        logger.success(f"company_data:{data}数据插入成功!!!")
    except Exception as e:
        logger.error(f"【save_company_data】保存失败！！失败详情：{e}")
        serv_db.rollback()


# for data in send_local_data():
#     save_company_copy(data)

"""copy filter:compSet key vaule"""
def copy_redis_key():
    res = conn.smembers("filter:compSet")
    for data in res:
        print(data.decode("utf-8"))
        conn.sadd("filter:with_compSet", data.decode("utf-8"))


# copy_redis_key()


"""删除服务器中mysql未下载的数据,通过mongo删除"""
def removeSameMoil():
    _ = 0
    y = 0
    # for keys in self.conn.scan_iter(match="福建省:*"):
    for keys in conn.scan_iter(match="福建省:三明市:大田县:*"):
        key = keys.decode("utf-8")
        cacheCode = key.split(":")[3]
        logger.info(cacheCode)
        datas = conn.smembers(key)
        # for data in list(datas)[692:]:
        for data in datas:
            info = json.loads(data)
            info["cacheCode"] = cacheCode
            logger.info(f"正在解析{info}")
            # if conn.sismember("filter:compSet",data):
            #     y+=1
            query = {
                'keys': info['company_name']
            }
            # 使用 find_one() 方法查询是否存在特定值的文档
            result = collection.find_one(query)
            # 如果结果不为 None，则表示值存在
            if result:
                logger.info(f"{info}数据重复！")
                y += 1
                # conn.srem("filter:compSet",info['company_name'])
            else:
                print(info['company_name'])
                conn.srem("filter:compSet", info['company_name'])
            _ += 1
        break
    logger.info(f"一共有{_}条数据！！")
    logger.info(f"有{y}重复数据数据！！")


# removeSameMoil()


"""服务器mysql的company_copy表导入服务器company报表"""
def serv_copy_serv():
    sql = "select * from company_copy;"
    # sql = "select * from  company LIMIT 2625,329;"
    serv_cursor.execute(sql)
    data = serv_cursor.fetchall()
    print(len(data))
    unique_data = set()
    result = []
    for item in data:
        if item[3] not in unique_data:
            result.append(item)
            unique_data.add(item[3])
    print(len(result))
    for original_tuple in result:
        new_tuple = (0,) + original_tuple[2:]
        res = conn.sadd("filter:compSet", str(new_tuple[2]))
        if res:
            logger.info(new_tuple)
            # Toservice_data(new_tuple)
        else:
            logger.error(f"数据重复:{new_tuple}")
        break

# cache_copy_data()


def local_dataToKey():
    sql = "select * from company;"
    # sql = "select * from  company LIMIT 2625,329;"
    # serv_cursor.execute(sql)
    serv_cursor.execute(sql)
    data = serv_cursor.fetchall()
    print(len(data))
    unique_data = set()
    result = []
    for item in data:
        # print(item[2])
        if item[2] not in unique_data:
            result.append(item)
            unique_data.add(item[2])
    print(len(result))
    for original_tuple in result:
        # new_tuple = (0,) + original_tuple[1:]
        # print(original_tuple[3])
        try:
            # pass

            collection.insert_one({'company_01': original_tuple[3]})
            print(original_tuple[3])
        except pymongo.errors.DuplicateKeyError:
            print("数据已存在，插入失败！")
        break
# local_dataToKey()


"""复制服务器表公司名作为redis和mongo"""
def filter_company():
    sql = "select * from company;"
    # sql = "select * from  company LIMIT 2625,329;"
    # serv_cursor.execute(sql)
    serv_cursor.execute(sql)
    data = serv_cursor.fetchall()
    print(len(data))
    unique_data = set()
    result = []
    for item in data:
        # print(item[2])
        if item[2] not in unique_data:
            result.append(item)
            unique_data.add(item[2])
    print(len(result))
    for original_tuple in result:
        company = original_tuple[2]
        print(company)
        conn.sadd("filter:compSet", company)
        try:
            collection_5_1.insert_one({'company': company})
            print("数据插入成功！")
        except pymongo.errors.DuplicateKeyError:
            print("数据已存在，插入失败！")
        # break


# filter_company()

collection_5_2 = client_1["CCDate_id"]["company"]
collection_5_3 = client_1["zhejiang"]["company"]
# resules1=list(collection_5_3.find())
# resules=list(collection_5_3.find())
pageSize = 50


# 司法  专利
def mongoToMQ(flg, item_info):
    collection_3 = client_1["TYCDate"]["rocrd"]
    credentials = pika.PlainCredentials('user', 'user123')  # 用户名和密码
    parameters = pika.ConnectionParameters(
        host='139.9.70.234',
        # RabbitMQ服务器地址
        port=5672,
        # RabbitMQ服务器端口，默认是5672
        virtual_host='/',
        # 虚拟主机，默认是'/'
        credentials=credentials,
        socket_timeout=100,
        heartbeat=300,
        retry_delay=300,
        connection_attempts=10
        # 用户名和密码
    )
    # 创建一个到RabbitMQ服务器的连接
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channe2 = connection.channel()
    channe3 = connection.channel()
    channe4 = connection.channel()
    channe5 = connection.channel()

    # 创建一个队列，如果不存在的话
    channel.queue_declare(queue='qqbx.dc.company', durable=True)
    channe2.queue_declare(queue='qqbx.dc.industry', durable=True)
    channe3.queue_declare(queue='qqbx.dc.qualification', durable=True)
    channe4.queue_declare(queue='qqbx.dc.judicial', durable=True)
    channe5.queue_declare(queue='qqbx.dc.property', durable=True)
    # l_json_data = [{
    #         "shortName": item_info["short_name"],
    #         "companyName": item_info["company_name"],
    #         "legalName": item_info["legal_name"],
    #         "legalTelephone": item_info["legal_telephone"],
    #         "companyAddress": item_info["company_address"],
    #         "registeredAddress": item_info["registered_address"],
    #         "companyPhone": item_info["company_phone"],
    #         "staffSize": item_info["staff_size"],
    #         "dateOfEstablishment": item_info["date_of_establishment"],
    #         "registeredCapital": item_info["registered_capital"],
    #         "contributedCapital": item_info["contributed_capital"],
    #         "businessScope": item_info["business_scope"],
    #         "registrationStatus": item_info["registration_status"],
    #         "tyxydm": item_info["tyxydm"],
    #         "nsrsbh": item_info["nsrsbh"],
    #         "zzjgdm": item_info["zzjgdm"],
    #         "yyqx": item_info["yyqx"],
    #         "companyType": item_info["company_type"],
    #         "registrationAuthority": item_info["registration_authority"],
    #         "gszch": item_info["gszch"],
    #         "nsrzz": item_info["nsrzz"],
    #         "provincialScope": None,
    #         "city":None,
    #         "areaCode":None
    #         }]

    # t_json_data = [{
    #         "shortName": item_info[1],
    #         "companyName": item_info[3],
    #         "legalName": item_info[4],
    #         "legalTelephone": item_info[5],
    #         "companyAddress": item_info[6],
    #         "companyPhone": item_info[8],
    #         "staffSize": item_info[9],
    #         "dateOfEstablishment": item_info[12].strftime("%Y-%m-%d %H:%M:%S"),
    #         "registeredCapital": item_info[17],
    #         "contributedCapital": item_info[18],
    #         "businessScope": item_info[19],
    #         "registrationStatus": item_info[20],
    #         "tyxydm": item_info[21],
    #         "nsrsbh": item_info[23],
    #         "zzjgdm": item_info[24],
    #         "yyqx": item_info[26],
    #         "companyType": item_info[27],
    #         "registrationAuthority": item_info[28],
    #         "gszch": item_info[22],
    #         "nsrzz": item_info[25],
    #         "city":None,
    #         "areaCode":None
    #         }]
    # json_data_1 =[{
    #     "relation_company_name":item_info["company_name"],
    #     "relation_industry_name":item_info["nameLevel2"],
    #     "relation_industry_pname":item_info["nameLevel1"],
    # }]
    # json_data_1 =[{
    #     "relation_company_name":item_info[7],
    #     "relation_industry_name":item_info[9],
    #     "relation_industry_pname":item_info[11],
    # }]
    # print(json_data_1)
    if flg == 1:
        try:
            # 发送消息到队列
            channel.basic_publish(exchange='',
                                  routing_key='qqbx.dc.company', body=json.dumps(item_info))
            logger.success(f"【* qqbx.dc.company】发送成功:{item_info}!!")
        except Exception as e:
            collection_7.insert_one(item_info)
    elif flg == 2:
        try:
            channe2.basic_publish(exchange='',
                                  routing_key='qqbx.dc.industry', body=json.dumps(item_info))
            logger.success(f"【*qqbx.dc.industry】发送成功:{item_info}!!")
        except Exception as e:
            collection_7_1.insert_one(item_info)
    elif flg == 3:
        try:
            channe3.basic_publish(exchange='', routing_key='qqbx.dc.qualification', body=json.dumps(item_info))
            logger.success(f"【*qqbx.dc.qualification】发送成功:{item_info} 发送成功！！")
        except Exception as e:
            collection_7_1.insert_one(item_info)
    elif flg == 4:
        try:
            # 司法
            logger.info(item_info)
            channe4.basic_publish(exchange='', routing_key='qqbx.dc.judicial', body=json.dumps(item_info))
            logger.success(f"judicial 司法数据 {item_info} 发送成功！！")
        except Exception as e:
            logger.error(e)
            collection_3.insert_one(item_info)
    else:
        try:
            # flg =5 专利
            logger.info(item_info)
            channe5.basic_publish(exchange='',
                                  routing_key='qqbx.dc.property', body=json.dumps(item_info))
            logger.success(f"property 专利数据 {item_info} 发送成功！！")
        except Exception as e:
            collection_3.insert_one(item_info)
    connection.close()


def send(currentPage):
    company_list = list()
    # for item in resules[page * 20:(page + 1) * 20]:
    data = collection_5_3.find({}, {"_id": False}).skip((currentPage - 1) * pageSize).limit(pageSize)
    _ = 0
    for item in data:
        # print(item)
        try:
            logger.info(f"keys是否存在:{'keys' in item}")
            if 'keys' in item:
                item_info = item["keys"]
                # logger.info(item_info)
                if item_info is None:
                    break
                # try:
                #     logger.info(item_info[2])
                #     # collection_5_1.insert_one({'company': item_info[2]})
                #     # collection_5.insert_one({"data":item_info})
                #     logger.success("数据插入成功！")
                # except pymongo.errors.DuplicateKeyError:
                #     logger.error("数据已存在，插入失败！")
                if len(item_info) == 29 or 31:
                    local_conn.sadd("shandong:filter:company", item_info[2])
                    # collection_5.insert_one({"data": item_info})
                    if item_info[16]:
                        if isinstance(item_info[16], str):
                            date_of_establishment = item_info[16]
                        else:
                            date_of_establishment = item_info[16].strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        date_of_establishment = None
                    if "oldCompanyNameList" not in item_info:
                        oldCompanyNameList = "[]"
                    else:
                        oldCompanyNameList = item_info[31]
                    data = {
                        "shortName": item_info[1],
                        "companyName": item_info[2],
                        "legalName": item_info[3],
                        "legalTelephone": item_info[4],
                        "companyAddress": item_info[6],
                        "companyPhone": item_info[9],
                        "staffSize": item_info[10],
                        "dateOfEstablishment": date_of_establishment,
                        "registeredCapital": item_info[17],
                        "contributedCapital": item_info[18],
                        "businessScope": item_info[19],
                        "registrationStatus": item_info[20],
                        "tyxydm": item_info[21],
                        "nsrsbh": item_info[23],
                        "zzjgdm": item_info[24],
                        "yyqx": item_info[26],
                        "companyType": item_info[27],
                        "registrationAuthority": item_info[28],
                        "gszch": item_info[22],
                        "nsrzz": item_info[25],
                        "city": item_info[29],
                        "areaCode": item_info[30],
                        "oldCompanyNameList": oldCompanyNameList
                    }
                    # else:
                    #     logger.warning(f"存在：{item_info[2]}")
                # 带公司id的值
                elif len(item_info) == 30:
                    if item_info[17]:
                        if isinstance(item_info[17], str):
                            date_of_establishment = item_info[17]
                        else:
                            date_of_establishment = item_info[17].strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        date_of_establishment = None
                    conn.sadd("filter:serv_company", item_info[3])
                    data = {
                        "shortName": item_info[2],
                        "companyName": item_info[3],
                        "legalName": item_info[4],
                        "legalTelephone": item_info[5],
                        "companyAddress": item_info[7],  # 7
                        "companyPhone": item_info[10],
                        "staffSize": item_info[11],
                        "dateOfEstablishment": date_of_establishment,
                        "registeredCapital": item_info[18],
                        "contributedCapital": item_info[19],
                        "businessScope": item_info[20],
                        "registrationStatus": item_info[21],
                        "tyxydm": item_info[22],
                        "nsrsbh": item_info[24],
                        "zzjgdm": item_info[25],
                        "yyqx": item_info[27],
                        "companyType": item_info[28],
                        "registrationAuthority": item_info[29],
                        "gszch": item_info[23],
                        "nsrzz": item_info[26],
                        "city": None,
                        "areaCode": None
                    }
                elif len(item_info) == 12:
                    try:
                        collection_6_1.insert_one({'keys': item_info[7]})
                        print("数据插入成功！")
                    except pymongo.errors.DuplicateKeyError:
                        print("数据已存在，插入失败！")
                    data1 = {
                        "relation_company_name": item_info[7],
                        "relation_industry_name": item_info[9],
                        "relation_industry_pname": item_info[11]
                    }
                    logger.info(data1)
                    # company_with_list.append(data1)
                else:
                    logger.error(len(item_info))
                    logger.error(item_info)
                    pass
                logger.info(data)
                company_list.append(data)
            else:
                with open("异常数据.json", "a", encoding="utf-8") as f:
                    f.write(item)
            _ += 1
        except Exception as e:
            logger.error(e)
            if "_id" in item:
                del item["_id"]
            collection_7.insert_one(item)
    logger.info(company_list)
    logger.info(len(company_list))
    mongoToMQ(1, company_list)
    logger.success(f"【*company】 第 {currentPage} 页发送成功！！")


# try:
#     company_with_list = list()
#     for item in resules1[page*20:(page+1)*20]:
#     # for item in resules1[:1]:
#     #     logger.info(f"keys是否存在:{'keys' in item}")
#         if "keys" in item:
#             item_info=tuple(item["keys"])
#             if item_info is None:
#                 break
#             conn.sadd("filter:with_compSet",item_info[7])
#             try:
#                 collection_6_1.insert_one({'company_with': item_info[7]})
#                 collection_6.insert_one({"data": item_info})
#                 logger.success("数据插入成功！")
#             except pymongo.errors.DuplicateKeyError:
#                 logger.error("数据已存在，插入失败！")
#                 pass
#             data1={
#             "relation_company_name":item_info[7],
#             "relation_industry_name":item_info[9],
#             "relation_industry_pname":item_info[11]
#             }
#             logger.info(data1)
#             company_with_list.append(data1)
#     logger.info(company_with_list)
#     # mongoToMQ(2,company_with_list)
#     logger.success(f"【*company_with】 第 {page+1} 页发送成功！！")
# except Exception as e:
#     collection_7_1.insert_one(item)
#     logger.error(e)
#     pass

# try:
#     qualification_list = list()
#     for item in resules2[page*20:(page+1)*20]:
#     # for item in resules2[:1]:
#         qualification_list.append(item)
#         if "_id" in item:
#             del item["_id"]
#         logger.info(item)
#     logger.info(qualification_list)
#     mongoToMQ(3,qualification_list)
#     logger.success(f"【*qualification】 第 {page+1} 页发送成功！！")
# except Exception as e:
#     collection_7_1.insert_one(item)
#     logger.error(e)
#     pass

# try:
#     judicial_with_list = list()
#     for item in resules[page*20:(page+1)*20]:
#         if "_id" in item:
#             del item["_id"]
#         # conn.sadd("filter:sfaj",item[7])
#         # try:
#             # collection_6_1.insert_one({'company_with': item_info[7]})
#             # collection_6.insert_one({"data": item_info})
#             # logger.success("数据插入成功！")
#         # except pymongo.errors.DuplicateKeyError:
#         #     logger.error("数据已存在，插入失败！")
#         #     pass
#         # data1 = {
#         #     "relationCompanyName": item["relation_company_name"],
#         #     "judicialType": "司法案件",
#         #     "judicialName": item["judicial_name"],
#         #     "judicialNumber": item["judicial_number"],
#         #     "history": item["history"],
#         #     "judicialUnit": item["judicial_unit"],
#         #     "recordDate": item["record_date"],
#         #     "filingDate": None,
#         #     "judicialMoney": None,
#         #     "infoType": None,
#         #     "judicialContent": None,
#         #     "sjmc": None,
#         #     "ajsf": item["ajsf"],
#         #     'otherIdentity': "[]",
#         #     "ay": item["ay"],
#         #     "sfDqslcx": item["sf_dqslcx"],
#         #     "xfXfdx": None,
#         #     "xfGldx": None,
#         #     "xfSql": None,
#         #     "bzxr": None,
#         #     "sxSxxw": None,
#         #     "sxLxqk": None,
#         #     "jyYcrq": None,
#         #     "jyYcyy": None,
#         #     "gqStatus": None
#         # }
#         logger.info(item)
#         judicial_with_list.append(item)
#         logger.success(f"【*judicial_with】 第 {page + 1} 页发送成功！！")
#     mongoToMQ(4, judicial_with_list)
# except Exception as e:
#     collection_7_1.insert_one(item)
#     pass

# try:
#     property_with_list = list()
#     for item in resules1[page*1:(page+1)*1]:
#         # for item in resules1[:1]:
#         if "_id" in item:
#             del item["_id"]
#         # conn.sadd("filter:with_compSet",item_info[7])
#         # try:
#         #     collection_6_1.insert_one({'company_with': item_info[7]})
#         #     collection_6.insert_one({"data": item_info})
#         #     logger.success("数据插入成功！")
#         # except pymongo.errors.DuplicateKeyError:
#         #     logger.error("数据已存在，插入失败！")
#         #     pass
#         data2 = {
#             "propertyType": "专利",
#             "propertyTitle": item["property_title"],
#             "propertyNum": item["property_num"],
#             "filingDate": item["filingDate"],
#             "gainDate": item["filingDate"],
#             "infoType": item["filingDate"],
#             "infoStatus": item["info_status"],
#             "content": None,
#             "relationCompanyName": item["relation_company_name"],
#             "sbImageUrl": None,
#             "zlInventor": item["zl_inventor"],
#             "zlOpenNum": item["zl_open_num"],
#             "rzSimpleName": None,
#             "rzVersionsNum": None,
#             "zpCompletionDate": None
#         }
#         logger.info(item)
#         # property_with_list.append(item)
#         logger.success(f"【*property_with】 第 {page + 1} 页发送成功！！")
#     # mongoToMQ(5,property_with_list)
# except Exception as e:
#     collection_8_1.insert_one(item)
#     pass
def localMongoToMQ():
    # 闽燕投资
    with ThreadPoolExecutor(3) as f:
        # send(1)
        futures = []
        for i in range(1, 50000):
            futures.append(f.submit(send, currentPage=i))
            logger.info(f"第 {i} 页数据")
            # break
            if len(futures) >= 100:
                for future in futures:
                    future.result()
                futures.clear()
        for future in futures:
            future.result()
# localMongoToMQ()

# data=(0, 1, '2024-06-11 16:30:13', None, None, None, None, '福安市晶唯一服装店', None, None, None, '批发业')
# item_info=(1, '奋安铝业', '奋安铝业股份有限公司', '黄奋', '2296713441', 350100,
#     '福州', 2, '福清市阳下街道洪宽工业村', '13850197273', '1601', 1,
#     datetime.datetime(2024, 4, 28, 11, 31, 20), 1, None, 0,
#     '1997-01-16', '50000万人民币', '50000万人民币',
#     '有色金属合金制造;有色金属压延加工;金属结构制造;门窗制造加工;合成材料制造;金属工具制造;钢压延加工;金属制日用品制造;金属链条及其他金属制品制造;汽车零部件研发;汽车零部件及配件制造;金属材料销售;高性能有色金属及合金材料销售;新型金属功能材料销售;合成材料销售;金属结构销售;有色金属合金销售;金属包装容器及材料销售;家具安装和维修服务;货物进出口;技术进出口;再生资源回收;再生资源加工;凭营业执照依法自主开展经营活动;道路货物运输',
#      '存续', '91350181260170698U', '350181100003305', '91350181260170698U', '26017069-8',
#      '一般纳税人', '1997-01-16\xa0至\xa0无固定期限', '股份有限公司(非上市、自然人投资或控股)', '福州市市场监督管理局')

# item_info={'short_name': '锡晖环境', 'company_name': '漳州市锡晖环境科技有限公司', 'legal_name': '杨珍', 'legal_telephone': 2003122853,
# 'company_address': '福建省漳州市南靖县奎洋镇永溪村319路48号', 'registered_address': '福建省漳州市南靖县奎洋镇永溪村319路48号',
# 'company_phone': '15106077573', 'staff_size': None, 'create_by': 1, 'create_datetime': '2024-06-07 10:18:16',
#  'date_of_establishment':  "1997-01-16", 'registered_capital': '100万人民币',
#  'contributed_capital': None, 'business_scope': '一般项目：环境保护专用设备制造；环保咨询服务；环境保护专用设备销售；工程和技术研究和试验发展；资源再生利用技术研发；资源循环利用服务技术咨询；专用化学产品销售（不含危险化学品）；化工产品销售（不含许可类化工产品）；国内贸易代理；生态环境材料销售；润滑油销售；新材料技术研发；生态环境材料制造；市政设施管理（除环境质量监测、污染源检查服务）；合成材料销售；污水处理及其再生利用（除环境质量检测、污染源检查服务）；信息技术咨询服务。（除依法须经批准的项目外，凭营业执照依法自主开展经营活动）许可项目：建设工程施工。（依法须经批准的项目，经相关部门批准后方可开展经营活动，具体经营项目以相关部门批准文件或许可证件为准）', 'registration_status': '存续', 'tyxydm': '91350627MA32PPPR9T', 'gszch': '350627100080137', 'nsrsbh': '91350627MA32PPPR9T', 'zzjgdm': 'MA32PPPR-9', 'yyqx': '2019-04-24\xa0至\xa02069-04-23', 'nameLevel2': None, 'nameLevel1': '专用设备制造业', 'registration_authority': '南靖县市场监督管理局', 'nsrzz': '增值税一般纳税人', 'company_type': '有限责任公司(自然人独资)'}
# mongoToMQ(1,data)

"""本地mysql数据库去重"""


def send_local_data():
    # i=42
    i = 3
    # i=1003
    while True:
        serv_cursor.execute(f"select * from  company LIMIT {1000 * i},1000")
        data = serv_cursor.fetchall()
        if not data:
            break
        unique_data = set()
        result = []
        for item in data:
            # print(item[2])
            if item[2] not in unique_data:
                result.append(item)
                unique_data.add(item[2])
        print("长度:", len(result))
        for original_tuple in result:
            try:
                date_str = original_tuple[16].strftime("%Y-%m-%d") if original_tuple[16] else None
                original_tuple = (0,) + original_tuple[1:16] + (date_str,) + original_tuple[17:]
                company_name = original_tuple[2]
                res = conn.sadd("filter:serv_company", company_name)
                try:
                    collection_5_1.insert_one({'company': company_name})
                    collection_5.insert_one({"data": original_tuple})
                    print("数据插入成功！")
                except pymongo.errors.DuplicateKeyError:
                    print("数据已存在，插入失败！")
                if res:
                    sql_code = "INSERT INTO company values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                               "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                               "%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    try:
                        serv_cursor.execute(sql_code, original_tuple)
                        serv_db.commit()
                        logger.success(f"company_data:{original_tuple}数据插入成功!!!")
                    except Exception as e:
                        logger.error(f"【*】保存失败！！失败详情：{e}")
                        serv_db.rollback()
                else:
                    logger.error(f"数据重复:{original_tuple}")
            except Exception as e:
                logger.error(f"数据处理出错：{e}")
                collection_7.insert_one("keys", original_tuple)
        logger.info(f"第 {i} 页")
        i += 1
        # if i==694:
        #     break


# send_local_data()


"""异步保存到本地 mysql company表"""


async def save_com_data(data, conn, cursor, semaphore):
    async with semaphore:
        sql_in = "INSERT INTO company() VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                 "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s," \
                 "%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            collection_5_1.insert_one({'company': data[2]})
            collection_5.insert_one({'company': data})
            logger.success(f'mongo 保存成功: {data} successfully into MongoDB')
        except pymongo.errors.DuplicateKeyError:
            logger.error("mongo保存失败！！")
        new_tuple = (0,) + tuple(data[1:])
        logger.info(new_tuple)
        try:
            await cursor.execute(sql_in, new_tuple)
            await conn.commit()
            await asyncio.sleep(random.randint(800, 1200) / 1000)
            logger.info(f'mysql company保存成功: {new_tuple} successfully into MySQL')
        except aiomysql.MySQLError as e:
            logger.error(f"mysql保存失败: {e} !!")
            await conn.rollback()


"""异步保存到到本地 mysql company_with表"""


async def save_com_with_data(data, conn, cursor, semaphore):
    async with semaphore:
        sql_code = "INSERT INTO company_industry_with_company() VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            collection_6_1.insert_one({'company_with': data[7]})
            collection_6.insert_one({'company_with': data})
            logger.info("Data inserted successfully into MongoDB!")
        except pymongo.errors.DuplicateKeyError:
            logger.error("Data already exists, insertion failed!")
        try:
            logger.info(data)
            await cursor.execute(sql_code, data)
            await conn.commit()
            logger.info(f"industry_data: {data} inserted successfully into MySQL!!!")
        except aiomysql.MySQLError as e:
            logger.error(f"Insertion failed: {e}")
            await conn.rollback()


"""获取mongo数据"""


async def main():
    semaphore = asyncio.Semaphore(10)
    pool = await aiomysql.create_pool(host='127.0.0.1', port=3306, user='root', password='root', db='test_01',
                                      minsize=1, maxsize=10)
    async with pool.acquire() as conn_1:
        async with conn_1.cursor() as cursor:
            results = list(collection_5.find())
            tasks = []
            for item in results:
                data = tuple(item["data"])
                if conn.sismember("filter:serv_company", data[2]):
                    logger.error("数据存在!!")
                else:
                    res = await save_com_data(data, conn_1, cursor, semaphore)
                    if res is not None:
                        conn.sadd("filter:serv_company", data[2])
                        task = asyncio.create_task(res)
                        tasks.append(task)
            await asyncio.sleep(random.randint(500, 800) / 1000)
            await asyncio.wait(tasks)
        await cursor.close()
    await pool.close()


# Run the main function
# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())


"""本地json文件导入redis，判断是否含中文字符"""


def contains_chinese(text):
    pattern = re.compile(r'[\u4e00-\u9fff]')  # 匹配中文字符的正则表达式范围
    return bool(pattern.search(text))


def saveMongo(item):
    if conn.sadd("filter:sifaComID_01", item):
        conn.lpush("all_company", item)


# with ThreadPoolExecutor(10) as f:
#     res = open("all.json", encoding="utf-8").read()
#     obj_list = []
#     for item in json.loads(res):
#         if contains_chinese(item['relation_company_name']):
#             data=str(item['relation_company_name']).replace(r"\xa0","")
#             print(data)
#             obj =f.submit(saveMongo,item=data)
#             obj_list.append(obj)
#
#     for future in as_completed(obj_list):
#         future.result()


def read_mongoDate():
    from pymongo import MongoClient
    client = MongoClient(host='192.168.5.167', port=27017)
    cli = client["CCDate"]["sfaj"]
    cli_1 = client["fujian"]["sifa"]
    pageSize = 1000;
    for currentPage in range(4700, 5000):
        for i in cli.find({}, {"_id": False}).skip((currentPage - 1) * pageSize).limit(pageSize):
            print(i)
            # aa = dict()
            # if "areaCode" in i:
            #     aa["province"]=i["province"]
            #     aa["city"]=i["city"]
            #     aa["areaCode"]=i["areaCode"]
            #     aa["briefName"]=i["briefName"]
            #     aa["base"]=i["base"]
            #     aa["new_day"]=i["new_day"]
            #     aa["next_day"]=i["next_day"]
            #     aa["new_date"]=i["new_date"]
            #     aa["next_day"]=i["next_day"]
            #     aa["company"]=i["company"]
            #     aa["id"]=i["id"]
            # else:
            #     aa["company"] = i["company"]
            #     aa["id"] = i["id"]
            cli_1.insert_one(i)
            # break


# read_mongoDate()


# 历史裁判文书     广州搜铺商业管理有限公司
#                浙江正见建设集团有限公司济南分公司

def copydata():
    while True:
        res = conn.lpop("参数过滤")
        if res is None:
            print("copy完成")
            break
        else:
            info = json.loads(res)
            print(info)
            if "company" in info:
                name = info["company"]
                res = local_conn.sadd("临时去重", name)
                if res:
                    local_conn.lpush("shanghai:company_id", json.dumps(info))
                    local_conn.sadd("shanghai:filter:company", info["company"])
                else:
                    logger.warning(f"存在重复数据:{info}")
            else:
                local_conn.sadd("shanghai:filter:params", json.dumps(info))

# local_T4_conn = redis.Redis(host='192.168.5.87', port=7933, db=0, password="fer@nhaweif576KUG",socket_connect_timeout=70)
# for i in range(5):
#     res=local_conn.lpop("sifaUser")
#     local_T4_conn.lpush("test1Mobil",res)

conn=pymongo.MongoClient(host='192.168.5.167', port=27017)
def copydata():
    with ThreadPoolExecutor(max_workers=4) as executor:
        conn["fujian"]['company'].create_index([('seq_num', pymongo.ASCENDING)])
        # 定义聚合管道
        pipeline = [
            {"$match": {"seq_num": {"$gte": 100}}},
            {"$sort": {"seq_num": pymongo.ASCENDING}},
            # {"$limit": 10}
        ]
        cursor = conn["fujian"]['sorcomp'].aggregate(pipeline, allowDiskUse=True).batch_size(50)
        for item in cursor:
            print(item)

def demo():
    client = pymongo.MongoClient(host='192.168.5.167', port=27017)
    client1 = pymongo.MongoClient(host='192.168.5.101', port=27017)
    collections = client1["anhui"].list_collection_names()
    print(collections)
    for collection in collections:
        col=client["anhui"][collection]
        col1 = client1["anhui"][collection]
        data=list(col.find())
        for i in data:
            del i["_id"]
            print(i)
            col1.insert_one(i)


if __name__ == "__main__":
    run_code = 0
    pass
