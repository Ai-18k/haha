#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :mongoCtrl.py
# @Time      :2024/11/22 12:56
# @Author    : 18k

import sys
import os
from pymongo.errors import ConnectionFailure

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)
# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)

"""遍历表的字段"""
import threading
from concurrent.futures import ThreadPoolExecutor
from ParseFile.detailparam import getdata
from MQitems.PikaUse import SendMQ
from loguru import logger
from queue import Queue
from pymongo import MongoClient, errors,WriteConcern


# serv_client = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",authSource="admin")
serv_client = MongoClient(host='192.168.5.167', port=27017)

# print(serv_client.list_database_names())

def filterkeys(db):
    s_dbs = serv_client[db].list_collection_names()
    print(s_dbs)
    for db2 in s_dbs:
        # print(db2)
        if db2=="fail_sifa_companyid":
            PolyWeightRemov(db,db2)

# 去重
# def PolyWeightRemov(key1,key2):
#     # Aggregation pipeline
#     pipeline = [
#         {
#             '$group': {
#                 # Group by the 'company' field
#                 'duplicates': {'$addToSet': '$_id'},  # Collect all _id values into an array
#                 'count': {'$sum': 1}  # Count occurrences of each group
#             }
#         },
#         {
#             '$match': {
#                 'count': {'$gt': 1}  # Match groups with more than one occurrence (duplicates)
#             }
#         },
#         {
#             '$project': {
#                 'duplicates': {
#                     '$slice': ['$duplicates', 1, {'$subtract': [{'$size': '$duplicates'}, 1]}]
#                 }
#             }
#         }
#     ]
#     cli = serv_client[key1][key2]
#     if key2=="company_id":
#         pipeline[0]['$group']['_id']={'company':'$company'}
#     elif  key2=="zlxx":
#         pipeline[0]['$group']['_id'] = {'relationCompanyName': '$relationCompanyName'}
#         pipeline[0]['$group']['_id'] = {'propertyNum': '$propertyNum'}
#     elif  key2=="被执行人":
#         pipeline[0]['$group']['_id'] = {'relationCompanyName': '$relationCompanyName'}
#         pipeline[0]['$group']['_id'] = {'judicialNumber': '$judicialNumber'}
#     elif key2=="fail_company_id":
#         pipeline[0]['$group']['_id'] = {'company': '$company'}
#         # pipeline[0]['$group']['_id'] = {'id': '$id'}
#     elif key2=="fail_sifa_companyid":
#         pipeline[0]['$group']['_id'] = {'company': '$company'}
#         pipeline[0]['$group']['_id'] = {'page': '$page'}
#     else:
#         return
#     # Execute the aggregation pipeline
#     results = list(cli.aggregate(pipeline, allowDiskUse=True))
#     # Remove the duplicates
#     for doc in results:
#         for duplicate_id in doc['duplicates']:
#             cli.delete_one({'_id': duplicate_id})
#
#     # Close the connection
#     serv_client.close()


def PolyWeightRemov01(key1, key2, page_size=1000):
    # Aggregation pipeline
    pipeline = [
        {
            '$group': {
                # 根据 key2 的值动态设置分组字段
                '_id': None,  # 默认值，稍后根据 key2 设置实际的分组字段
                'duplicates': {'$addToSet': '$_id'},  # 将重复的 _id 存入一个集合
                'count': {'$sum': 1}  # 计数每个组的文档数量
            }
        },
        {
            '$match': {
                'count': {'$gt': 1}  # 找出重复的文档组
            }
        },
        {
            '$project': {
                'duplicates': {
                    '$slice': ['$duplicates', 1, {'$subtract': [{'$size': '$duplicates'}, 1]}]  # 排除每组中的第一个文档，只保留重复文档的 _id
                }
            }
        }
    ]

    # 根据 key2 来调整分组依据
    if key2 == "company_id":
        pipeline[0]['$group']['_id'] = {'company': '$company'}
    elif key2 == "zlxx":
        pipeline[0]['$group']['_id'] = {'relationCompanyName': '$relationCompanyName'}
        pipeline[0]['$group']['_id'] = {'propertyNum': '$propertyNum'}
    elif key2 == "被执行人":
        pipeline[0]['$group']['_id'] = {'relationCompanyName': '$relationCompanyName'}
        pipeline[0]['$group']['_id'] = {'judicialNumber': '$judicialNumber'}
    elif key2 == "fail_company_id":
        pipeline[0]['$group']['_id'] = {'company': '$company'}
    elif key2 == "fail_sifa_companyid":
        pipeline[0]['$group']['_id'] = {'company': '$company'}
        pipeline[0]['$group']['_id'] = {'page': '$page'}
    else:
        return  # 如果没有匹配的 key2，退出函数

    # 获取数据库连接
    cli = serv_client[key1][key2]

    # 分页查询的初始偏移量
    skip = 0
    while True:
        # 增加分页阶段
        paginated_pipeline = pipeline + [
            {'$skip': skip},  # 跳过前 skip 条记录
            {'$limit': page_size}  # 限制每次查询返回的文档数量
        ]

        # 执行聚合操作
        results = list(cli.aggregate(paginated_pipeline, allowDiskUse=True))

        if not results:
            break  # 如果没有返回数据，退出循环

        # 执行删除操作
        for doc in results:
            for duplicate_id in doc['duplicates']:
                cli.delete_one({'_id': duplicate_id})

        # 增加分页偏移量
        skip += page_size

    # 关闭数据库连接
    serv_client.close()


def PolyWeightRemov(key1, key2, page_size=1000):
    # 聚合管道
    pipeline = [
        {
            '$group': {
                '_id': None,  # 分组条件
                'duplicates': {'$addToSet': '$_id'},  # 将重复的 _id 加入集合
                'count': {'$sum': 1}  # 统计每个组的文档数
            }
        },
        {
            '$match': {
                'count': {'$gt': 1}  # 找出重复文档
            }
        },
        {
            '$project': {
                'duplicates': {
                    '$slice': ['$duplicates', 1, 1000]  # 每次只保留最多1000个重复项
                }
            }
        }
    ]

    # 根据 key2 设置不同的分组依据
    if key2 == "company_id":
        pipeline[0]['$group']['_id'] = {'company': '$company'}
    elif key2 == "zlxx":
        pipeline[0]['$group']['_id'] = {'relationCompanyName': '$relationCompanyName'}
        pipeline[0]['$group']['_id'] = {'propertyNum': '$propertyNum'}
    elif key2 == "被执行人":
        pipeline[0]['$group']['_id'] = {'relationCompanyName': '$relationCompanyName'}
        pipeline[0]['$group']['_id'] = {'judicialNumber': '$judicialNumber'}
    elif key2 == "fail_company_id":
        pipeline[0]['$group']['_id'] = {'company': '$company'}
    elif key2 == "fail_sifa_companyid":
        pipeline[0]['$group']['_id'] = {'company': '$company'}
        pipeline[0]['$group']['_id'] = {'page': '$page'}
    else:
        return  # 如果没有匹配的 key2，退出函数

    # 获取数据库连接
    cli = serv_client[key1][key2]

    # 分页处理
    skip = 0
    while True:
        # 增加分页阶段
        paginated_pipeline = pipeline + [
            {'$skip': skip},  # 跳过前 skip 条记录
            {'$limit': page_size}  # 限制每次查询返回的文档数量
        ]

        # 执行聚合操作
        results = list(cli.aggregate(paginated_pipeline, allowDiskUse=True))

        if not results:
            break  # 如果没有返回数据，退出循环

        # 执行删除操作
        for doc in results:
            for duplicate_id in doc['duplicates']:
                cli.delete_one({'_id': duplicate_id})

        # 增加分页偏移量
        skip += page_size

    # 关闭数据库连接
    serv_client.close()


filterkeys("zhejiang")


local_client = MongoClient(host='127.0.0.1', port=27017)
write_concern = WriteConcern(w=1)
source_client = MongoClient(host='192.168.5.167', port=27017)
target_client = MongoClient(host='192.168.5.70', port=27017)

def copyMongo():
    try:
        # 列出源数据库的所有数据库
        source_dbs = source_client.list_database_names()
        for db_name in source_dbs:
            # 排除特定的数据库
            if not db_name.startswith(("CCDate", "CCDate_id", 'CheckGaps',
                                       'TYCDate', 'admin', 'config', 'filter',
                                       'local','property', 'sfaj', "judicial",
                                       # "anhui",
                                       # "beijing",
                                       # "chongqing",
                                       # "fujian",
                                       # "gansu",
                                       # "guangxi",
                                       # "guangdong",
                                       # "guizhou",
                                       # "hainan",
                                       # "hebei",
                                       # "heilongjiang",
                                       # "henan",
                                       # "hubei",
                                       # "hunan",
                                       # "jiangsu",
                                       # "jiangxi",
                                       # "jilin",
                                       # "liaoning",
                                       # "neimenggu",
                                       # "ningxia",
                                       # "qinghai",
                                       # "sanxi",
                                       # "shandong",
                                       # "shanghai",
                                       # "shanxi",
                                       # "sichuan",
                                       # "tianjin",
                                       # "xinjiang",
                                       # "xizang",
                                       # "yunnan",
                                       # "zhejiang",
                                       # "taiwan",
                                       # "xianggang"
                                       )):
                print(f"开始复制数据库: {db_name}")

                # 获取源数据库和目标数据库
                old_db = source_client[db_name]
                new_db = target_client[db_name]

                # 列出源数据库中的所有集合
                collection_names = old_db.list_collection_names()

                for collection_name in collection_names:
                    if collection_name in [
                            # "company_id",
                            # "sorcomp",
                            # "电信许可",
                            # "裁判文书",
                            # "商标信息",
                            # "资质证书",
                            # "作品著作权",
                            # "行政许可",
                            # "软著著作权",
                            "company",
                            "company_qualification",
                            "company_with",
                            "sfaj",
                            "sifa",
                            "zlxx",
                            "法院公告",
                            "股权冻结",
                            "经营异常",
                            "限制消费",
                            "失信被执行人",
                            "行政处罚",
                            "裁判文书",
                            "被执行人",
                            "历史被执行人",
                            "历史裁判文书",
                            "历史法院公告",
                            "历史股权冻结",
                            "历史股权冻结",
                            "历史经营异常",
                            "历史失信被执行人",
                            "历史限制消费",
                            "历史行政处罚",
                            "fail_商标信息", "fail_电信许可", "fail_历史sifa_companyid", "fail_软著著作权","fail_company_id",
                            "fail_行政许可", "fail_资质证书", "fail_作品著作权", "fail_judicial_with",
                            "fail_property_with", "fail_sifa_companyid", "fail_地区时间参数", "公司详情失败公司id"]:
                        print(f"{collection_name}:已经完成迁移！！")
                    else:
                        print(f"复制集合: {collection_name}")

                        old_collection = old_db[collection_name]
                        new_collection = new_db[collection_name]

                        # 删除目标集合中的所有数据
                        new_collection.delete_many({})

                        # 复制索引（如果有的话）
                        indexes = old_collection.index_information()
                        for index_name, index_info in indexes.items():
                            if index_name != '_id_':  # 跳过默认的 _id 索引
                                new_collection.create_index(index_info['key'])

                        # 复制数据：批量插入
                        currentPage = 0
                        pageSize = 1000
                        last_id = None  # 用于存储上一批数据的最后一个文档的 _id

                        while True:
                            query = {}
                            if last_id:
                                query["_id"] = {"$gt": last_id}  # 基于 _id 分页

                            # 根据 _id 排序，确保数据按照插入顺序分页
                            docs_cursor = old_collection.find(query).sort("_id", 1).limit(pageSize)
                            docs = list(docs_cursor)

                            if not docs:  # 如果没有数据，退出循环
                                print(f"{db_name}.{collection_name} 没有更多数据需要复制。")
                                break

                            # 批量插入数据到目标集合
                            new_collection.with_options(write_concern=write_concern).insert_many(docs)
                            print(f"成功复制 {(currentPage + 1) * pageSize} 条数据到 {db_name}.{collection_name}")

                            # 更新 last_id 和页码
                            last_id = docs[-1]["_id"]
                            currentPage += 1
    except errors.ConnectionFailure:
        print("无法连接到 MongoDB 服务器。请检查网络连接。")
    except Exception as e:
        print(f"出现错误: {e}")

# 执行数据迁移
# copyMongo()


class A:
    source_client = MongoClient(host='192.168.5.167', port=27017)
    target_client = MongoClient(host='192.168.5.70', port=27017)

    def copy_collection(self,db_name, collection_name):
        try:
            print(f"复制集合: {collection_name}")
            old_db = self.source_client[db_name]
            new_db = self.target_client[db_name]
            old_collection = old_db[collection_name]
            new_collection = new_db[collection_name]

            # 删除目标集合中的所有数据
            new_collection.delete_many({})

            # 复制索引（如果有的话）
            indexes = old_collection.index_information()
            for index_name, index_info in indexes.items():
                if index_name != '_id_':  # 跳过默认的 _id 索引
                    new_collection.create_index(index_info['key'])

            # 复制数据：批量插入
            currentPage = 0
            pageSize = 1000
            last_id = None  # 用于存储上一批数据的最后一个文档的 _id

            while True:
                query = {}
                if last_id:
                    query["_id"] = {"$gt": last_id}  # 基于 _id 分页

                # 根据 _id 排序，确保数据按照插入顺序分页
                docs_cursor = old_collection.find(query).sort("_id", 1).limit(pageSize)
                docs = list(docs_cursor)

                if not docs:  # 如果没有数据，退出循环
                    print(f"{db_name}.{collection_name} 没有更多数据需要复制。")
                    break

                # 批量插入数据到目标集合
                new_collection.insert_many(docs)
                print(f"成功复制 {(currentPage + 1) * pageSize} 条数据到 {db_name}.{collection_name}")

                # 更新 last_id 和页码
                last_id = docs[-1]["_id"]
                currentPage += 1
        except Exception as e:
            print(f"复制 {db_name}.{collection_name} 时出现错误: {e}")

    def copy_mongo_multithreaded(self):
        try:
            source_dbs = self.source_client.list_database_names()
            threads = []
            with ThreadPoolExecutor(max_workers=5) as f:
                for db_name in source_dbs:
                    if not db_name.startswith(("CCDate", "CCDate_id", 'CheckGaps',
                                               'TYCDate', 'admin', 'config', 'filter',
                                               'local', 'property', 'sfaj', "judicial",
                                              "anhui",
                                              # "beijing",
                                              # "chongqing",
                                              # "fujian",
                                              # "gansu",
                                              # "guangxi",
                                              # "guangdong",
                                              # "guizhou",
                                              # "hainan",
                                              # "hebei",
                                              # "heilongjiang",
                                              # "henan",
                                              # "hubei",
                                              # "hunan",
                                              # "jiangsu",
                                              # "jiangxi",
                                              # "jilin",
                                              # "liaoning",
                                              # "neimenggu",
                                              # "ningxia",
                                              # "qinghai",
                                              # "sanxi",
                                              # "shandong",
                                              # "shanghai",
                                              # "shanxi",
                                              # "sichuan",
                                              # "tianjin",
                                              # "xinjiang",
                                              # "xizang",
                                              # "yunnan",
                                              # "zhejiang",
                                              # "taiwan",
                                              "xianggang"
                                               )):
                        print(f"开始复制数据库: {db_name}")
                        old_db = self.source_client[db_name]
                        collection_names = old_db.list_collection_names()
                        for collection_name in collection_names:
                            if collection_name in [
                                # "company_id",
                                # "sorcomp",
                                # "电信许可",
                                # "裁判文书",
                                # "商标信息",
                                # "资质证书",
                                # "作品著作权",
                                # "行政许可",
                                # "软著著作权",
                                "company",
                                "company_qualification",
                                "company_with",
                                "sfaj",
                                "sifa",
                                "zlxx",
                                "法院公告",
                                "股权冻结",
                                "经营异常",
                                "限制消费",
                                "失信被执行人",
                                "行政处罚",
                                "裁判文书",
                                "被执行人",
                                "历史被执行人",
                                "历史裁判文书",
                                "历史法院公告",
                                "历史股权冻结",
                                "历史股权冻结",
                                "历史经营异常",
                                "历史失信被执行人",
                                "历史限制消费",
                                "历史行政处罚",
                                "fail_商标信息", "fail_电信许可", "fail_历史sifa_companyid", "fail_软著著作权",
                                "fail_company_id",
                                "fail_行政许可", "fail_资质证书", "fail_作品著作权", "fail_judicial_with",
                                "fail_property_with", "fail_sifa_companyid", "fail_地区时间参数", "公司详情失败公司id"]:
                                print(f"{collection_name}:已经完成迁移！！")
                            else:
                                print(f"复制集合: {collection_name}")
                                threads.append(f.submit(self.copy_collection,db_name=db_name, collection_name=collection_name))
                for thread in threads:
                    thread.result()

        except ConnectionFailure:
            print("无法连接到 MongoDB 服务器。请检查网络连接。")
        except Exception as e:
            print(f"出现错误: {e}")

# 执行多线程数据迁移
# A().copy_mongo_multithreaded()

class B:
    source_client = MongoClient(host='192.168.5.167', port=27017)
    target_client = MongoClient(host='192.168.5.70', port=27017)

    def copy_collection(self,db_name, collection_name):
        try:
            print(f"复制集合: {collection_name}")
            old_db = self.source_client[db_name]
            new_db = self.target_client[db_name]
            old_collection = old_db[collection_name]
            new_collection = new_db[collection_name]

            # 删除目标集合中的所有数据
            new_collection.delete_many({})

            # 复制索引（如果有的话）
            indexes = old_collection.index_information()
            for index_name, index_info in indexes.items():
                if index_name != '_id_':  # 跳过默认的 _id 索引
                    new_collection.create_index(index_info['key'])

            # 复制数据：批量插入
            currentPage = 0
            pageSize = 1000
            last_id = None  # 用于存储上一批数据的最后一个文档的 _id

            while True:
                query = {}
                if last_id:
                    query["_id"] = {"$gt": last_id}  # 基于 _id 分页

                # 根据 _id 排序，确保数据按照插入顺序分页
                docs_cursor = old_collection.find(query).sort("_id", 1).limit(pageSize)
                docs = list(docs_cursor)

                if not docs:  # 如果没有数据，退出循环
                    print(f"{db_name}.{collection_name} 没有更多数据需要复制。")
                    break

                # 批量插入数据到目标集合
                new_collection.insert_many(docs)
                print(f"成功复制 {(currentPage + 1) * pageSize} 条数据到 {db_name}.{collection_name}")

                # 更新 last_id 和页码
                last_id = docs[-1]["_id"]
                currentPage += 1
        except Exception as e:
            print(f"复制 {db_name}.{collection_name} 时出现错误: {e}")

    def copy_mongo_multithreaded(self):
        try:
            source_dbs = self.source_client.list_database_names()
            threads = []
            pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
            for db_name in source_dbs:
                if not db_name.startswith(("CCDate", "CCDate_id", 'CheckGaps',
                                               'TYCDate', 'admin', 'config', 'filter',
                                               'local', 'property', 'sfaj', "judicial",
                                              "anhui",
                                              "beijing",
                                              "chongqing",
                                              "fujian",
                                              "gansu",
                                              "guangxi",
                                              "guangdong",
                                              "guizhou",
                                              "hainan",
                                              "hebei",
                                              "heilongjiang",
                                              "henan",
                                              "hubei",
                                              "hunan",
                                              "jiangsu",
                                              "jiangxi",
                                              "jilin",
                                              "liaoning",
                                              "neimenggu",
                                              "ningxia",
                                              "qinghai",
                                              "sanxi",
                                              "shandong",
                                              "shanghai",
                                              "shanxi",
                                              "sichuan",
                                              "tianjin",
                                              "xinjiang",
                                              "xizang",
                                              "yunnan",
                                              "zhejiang",
                                              "taiwan",
                                              # "xianggang"
                                           )):
                    print(f"开始复制数据库: {db_name}")
                    old_db = self.source_client[db_name]
                    collection_names = old_db.list_collection_names()

                    for collection_name in collection_names:
                        if collection_name in [
                            # "company_id",
                            # "sorcomp",
                            # "电信许可",
                            # "裁判文书",
                            # "商标信息",
                            # "资质证书",
                            # "作品著作权",
                            # "行政许可",
                            # "软著著作权",
                            "company",
                            "company_qualification",
                            "company_with",
                            "sfaj",
                            "sifa",
                            "zlxx",
                            "法院公告",
                            "股权冻结",
                            "经营异常",
                            "限制消费",
                            "失信被执行人",
                            "行政处罚",
                            "裁判文书",
                            "被执行人",
                            "历史被执行人",
                            "历史裁判文书",
                            "历史法院公告",
                            "历史股权冻结",
                            "历史股权冻结",
                            "历史经营异常",
                            "历史失信被执行人",
                            "历史限制消费",
                            "历史行政处罚",
                            "fail_商标信息", "fail_电信许可", "fail_历史sifa_companyid", "fail_软著著作权",
                            "fail_company_id",
                            "fail_行政许可", "fail_资质证书", "fail_作品著作权", "fail_judicial_with",
                            "fail_property_with", "fail_sifa_companyid", "fail_地区时间参数", "公司详情失败公司id"]:
                            print(f"{collection_name}:已经完成迁移！！")
                        else:
                            print(f"复制集合: {collection_name}")
                            pool.apply_async(self.copy_collection, args=(db_name, collection_name,))
            pool.close()
            pool.join()
            print("所有数据库处理完成。")
        except ConnectionFailure:
            print("无法连接到 MongoDB 服务器。请检查网络连接。")
        except Exception as e:
            print(f"出现错误: {e}")

# 执行多进程数据迁移
# B().copy_mongo_multithreaded()


import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
class C:
    source_client = AsyncIOMotorClient(host='192.168.5.167', port=27017)
    target_client = AsyncIOMotorClient(host='192.168.5.70', port=27017)

    async def copy_collection(self,db_name, collection_name):
        try:
            print(f"复制集合: {collection_name}")
            old_db = self.source_client[db_name]
            new_db = self.target_client[db_name]
            old_collection = old_db[collection_name]
            new_collection = new_db[collection_name]

            # 删除目标集合中的所有数据
            await new_collection.delete_many({})

            # 复制索引（如果有的话）
            indexes = await old_collection.index_information()
            for index_name, index_info in indexes.items():
                if index_name != '_id_':  # 跳过默认的 _id 索引
                    await new_collection.create_index(index_info['key'])

            # 复制数据：批量插入
            currentPage = 0
            pageSize = 1000
            last_id = None  # 用于存储上一批数据的最后一个文档的 _id

            while True:
                query = {}
                if last_id:
                    query["_id"] = {"$gt": last_id}  # 基于 _id 分页

                # 根据 _id 排序，确保数据按照插入顺序分页
                docs_cursor = old_collection.find(query).sort("_id", 1).limit(pageSize)
                docs = await docs_cursor.to_list(length=pageSize)

                if not docs:  # 如果没有数据，退出循环
                    print(f"{db_name}.{collection_name} 没有更多数据需要复制。")
                    break

                # 批量插入数据到目标集合
                await new_collection.insert_many(docs)
                print(f"成功复制 {(currentPage + 1) * pageSize} 条数据到 {db_name}.{collection_name}")

                # 更新 last_id 和页码
                last_id = docs[-1]["_id"]
                currentPage += 1

        except Exception as e:
            print(f"复制 {db_name}.{collection_name} 时出现错误: {e}")

    async def copy_mongo_async(self):
        try:
            # 获取源数据库列表
            source_dbs = await self.source_client.list_database_names()

            for db_name in source_dbs:
                # 跳过一些系统数据库
                if not db_name.startswith(("CCDate", "CCDate_id", 'CheckGaps',
                                               'TYCDate', 'admin', 'config', 'filter',
                                               'local', 'property', 'sfaj', "judicial",
                                              "anhui",
                                              "beijing",
                                              "chongqing",
                                              "fujian",
                                              "gansu",
                                              "guangxi",
                                              "guangdong",
                                              "guizhou",
                                              "hainan",
                                              "hebei",
                                              "heilongjiang",
                                              "henan",
                                              "hubei",
                                              "hunan",
                                              "jiangsu",
                                              "jiangxi",
                                              "jilin",
                                              "liaoning",
                                              "neimenggu",
                                              "ningxia",
                                              "qinghai",
                                              "sanxi",
                                              "shandong",
                                              "shanghai",
                                              "shanxi",
                                              "sichuan",
                                              "tianjin",
                                              "xinjiang",
                                              "xizang",
                                              "yunnan",
                                              "zhejiang",
                                              # "taiwan",
                                              "xianggang"
                                           )):
                    print(f"开始复制数据库: {db_name}")
                    old_db = self.source_client[db_name]
                    collection_names = await old_db.list_collection_names()

                    for collection_name in collection_names:
                        if collection_name in [
                            # "company_id",
                            "sorcomp",
                            "电信许可",
                            "裁判文书",
                            "商标信息",
                            "资质证书",
                            "作品著作权",
                            "行政许可",
                            "软著著作权",
                            "company",
                            "company_qualification",
                            "company_with",
                            "sfaj",
                            "sifa",
                            "zlxx",
                            "法院公告",
                            "股权冻结",
                            "经营异常",
                            "限制消费",
                            "失信被执行人",
                            "行政处罚",
                            "裁判文书",
                            "被执行人",
                            "历史被执行人",
                            "历史裁判文书",
                            "历史法院公告",
                            "历史股权冻结",
                            "历史股权冻结",
                            "历史经营异常",
                            "历史失信被执行人",
                            "历史限制消费",
                            "历史行政处罚",
                            "fail_商标信息", "fail_电信许可", "fail_历史sifa_companyid", "fail_软著著作权",
                            "fail_company_id",
                            "fail_行政许可", "fail_资质证书", "fail_作品著作权", "fail_judicial_with",
                            "fail_property_with", "fail_sifa_companyid", "fail_地区时间参数", "公司详情失败公司id"]:
                            print(f"{collection_name}:已经完成迁移！！")
                        else:
                            print(f"复制集合: {collection_name}")
                            # 为每个集合创建任务进行复制
                            await self.copy_collection(db_name, collection_name)

        except ConnectionFailure:
            print("无法连接到 MongoDB 服务器。请检查网络连接。")
        except Exception as e:
            print(f"出现错误: {e}")

# 执行异步数据迁移
# loop = asyncio.get_event_loop()
# loop.run_until_complete(C().copy_mongo_async())


"""多线程处理"""
def mbc():
    source_client = MongoClient(host='192.168.5.167', port=27017)
    target_client = MongoClient(host='192.168.5.70', port=27017)

    def test(target_client,db, db1, dbcoursor):
        num=dbcoursor.estimated_document_count({})-target_client[db][db1].estimated_document_count({})
        if num>0:
            print(f"新增：{db}:{db1}",num)
            return f"{db}:{db1}"

    countNum=list()
    with ThreadPoolExecutor(max_workers=5) as f:
        source_dbs = source_client.list_database_names()
        for db in source_dbs:
            if not db.startswith(("CCDate", "CCDate_id", 'CheckGaps',
                                           'TYCDate', 'admin', 'config', 'filter',
                                           'local','property', 'sfaj', "judicial",
                                           )):
                print(f"开始统计数据库: {db}")
                # 获取源数据库和目标数据库
                old_db = source_client[db]
                # new_db = target_client[db]
                # 列出源数据库中的所有集合
                collection_names = old_db.list_collection_names()
                for db1 in collection_names:
                    dbcoursor=source_client[db][db1]
                    # print(f"{db}:{db1}",dbcoursor.count_documents({}))
                    # print(f"{db}:{db1}",dbcoursor.estimated_document_count({}))
                    countNum.append(f.submit(test,target_client=target_client,db=db,db1=db1,dbcoursor=dbcoursor))
        for task in countNum:
            result=task.result()
            print("需要更新库：",result)
mbc()


"""多进程处理"""
import multiprocessing
from pymongo import MongoClient
class ProcessmbcV1:

    # 创建MongoDB客户端
    local_client = MongoClient(host='127.0.0.1', port=27017)

    # 进程池执行的任务
    def test(self,db, db1):
        try:
            print(f"正在处理数据库: {db}，集合: {db1}")  # 调试输出
            collection = local_client[db][db1]
            count = collection.estimated_document_count({})
            print(f"{db}:{db1} => 文档数量: {count}")  # 输出数量
        except Exception as e:
            print(f"处理 {db}:{db1} 时出错: {e}")  # 错误输出

    def mbc(self):
        # 创建进程池
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        source_dbs = local_client.list_database_names()
        for db in source_dbs:
            if not db.startswith(("CCDate", "CCDate_id", 'CheckGaps',
                                  'TYCDate', 'admin', 'config', 'filter',
                                  'local', 'property', 'sfaj', "judicial")):
                print(f"开始处理数据库: {db}")
                collection_names = local_client[db].list_collection_names()
                for db1 in collection_names:
                    # 将任务添加到进程池
                    pool.apply_async(self.test, args=(db, db1,))

        pool.close()
        pool.join()
        print("所有数据库处理完成。")
# ProcessmbcV1().mbc()


"""异步处理"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
class AsynciombcV2(object):
    # 创建异步MongoDB客户端
    local_client = AsyncIOMotorClient("mongodb://192.168.5.167:27017")

    # 异步执行查询操作的任务
    async def test(self, db, db1):
        collection = self.local_client[db][db1]
        count = await collection.estimated_document_count({})
        print(f"{db}:{db1} => {count}")

    async def mbc(self):
        # 异步获取数据库列表
        source_dbs = await self.local_client.list_database_names()  # 加上 await
        tasks = []
        for db in source_dbs:
            if not db.startswith(("CCDate", "CCDate_id", 'CheckGaps',
                                  'TYCDate', 'admin', 'config', 'filter',
                                  'local', 'property', 'sfaj', "judicial")):
                print(f"开始处理数据库: {db}")
                # 获取数据库集合并创建任务
                collection_names = await self.local_client[db].list_collection_names()  # 加上 await
                for db1 in collection_names:
                    tasks.append(self.test(db, db1))

        # 异步执行所有任务
        await asyncio.gather(*tasks)

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
    # AsynciombcV2().mbc()
    # CompanySend().keysiter()
    # filterkeys("zhejiang")
    # ProcessmbcV1().mbc()
    # asyncio.run(AsynciombcV2().mbc())
    # B().copy_mongo_multithreaded()
    run_code = 0
    pass



