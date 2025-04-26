#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
import pymongo
import logging
import datetime
import re

from pymongo import errors

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('redis_to_mongo_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 重复键记录文件
DUPLICATE_FILE = f'duplicates_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

# Redis 连接配置
REDIS_HOST = '192.168.5.167'
REDIS_PORT = 10824
REDIS_PASSWORD = 'e8Mzr}$%jsuCxKn4r#mm'
REDIS_DB = 0

# MongoDB 连接配置
MONGO_HOST = '192.168.5.167'
MONGO_PORT = 27017

def connect_to_redis():
    """连接到 Redis 服务器"""
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=True  # 自动将字节解码为字符串
        )
        client.ping()  # 测试连接
        logger.info("成功连接到 Redis")
        return client
    except Exception as e:
        logger.error(f"Redis 连接失败: {e}")
        raise

def connect_to_mongodb():
    """连接到 MongoDB 服务器"""
    try:
        client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        # 测试连接
        client.admin.command('ping')
        logger.info("成功连接到 MongoDB")
        return client
    except Exception as e:
        logger.error(f"MongoDB 连接失败: {e}")
        raise

def print_guangxi_filter_data(area,redis_client,mongo_client):
    """查找并打印 guangxi:filter 下的所有键和对应的集合数据"""
    try:
        # 查找所有以 guangxi:filter 开头的键
        # area="guangxi"
        pattern = area+":filter*"
        keys = redis_client.keys(pattern)
        
        if not keys:
            logger.info(f"未找到任何匹配 '{pattern}' 的键")
            return

        logger.info(f"找到 {len(keys)} 个匹配 '{pattern}' 的键")
        
        # 遍历每个键并获取其集合数据
        for key in keys:
            # if key=="fujian:filter:company_id":
                rr = key.split(":")
                momgkey = rr[-2] + "_" + rr[-1]
                print(momgkey)
                logger.info(f"处理键: {key}")
                # 获取该键对应的集合所有成员
                members = redis_client.smembers(key)

                if not members:
                    logger.info(f"键 '{key}' 对应的集合为空")
                    continue
                db= mongo_client[area][momgkey]
                db.create_index([('company', pymongo.ASCENDING)], unique=True)
                logger.info(f"键 '{key}' 包含 {len(members)} 条数据:")
                for member in members:
                    print(f"  {member}")
                    try:
                        db.insert_one({"company":member})
                        print("数据插入成功！")
                    except errors.DuplicateKeyError:
                        print("数据已存在，插入失败！")
                print("-" * 50)  # 分隔不同的键的数据
            # else:
            #     continue
    
    except Exception as e:
        logger.error(f"获取 {area}+:filter 数据时出错: {e}")


def main():
    """主函数"""
    try:
        # 连接 Redis 和 MongoDB
        redis_client = connect_to_redis()
        mongo_client = connect_to_mongodb()
        
        # 执行查找和打印 guangxi:filter 数据的函数
        arealist=[
                # "beijing",
                # "chongqing",
                #"fujian",
                # "guizhou",
                # "hainan",
                # "hebei",
                # "hubei",
                # "jiangsu",
                # "jiangxi",
                # "jilin",
                # "neimenggu",
                # "ningxia",
                # "sanxi",
                # "shandong",
                # "shanghai",
                # "shanxi",
                # "xinjiang",
                # "xizang",
                # "zhejiang",
                # "liaoning",
                # "sichuan",
                # "hunan",
                # "guangxi",
                # "anhui",
                # "henan",
                # "yunnan",
                # "guangdong",
                # "heilongjiang",
                "qinghai",
                # "tianjin",
                # "gansu",
                # "taiwan",
                # "xianggang"
        ]
        for area in arealist:
            print_guangxi_filter_data(area,redis_client,mongo_client)

        # 完成后关闭连接
        redis_client.close()
        mongo_client.close()
        logger.info("操作完成")
    
    except Exception as e:
        logger.error(f"程序执行出错: {e}")

if __name__ == "__main__":
    main()

