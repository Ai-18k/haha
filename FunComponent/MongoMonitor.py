# _*_ coding:UTF-8 _*


""" Mongo service statusMonitor """

from pymongo import MongoClient
import os
from pymongo.errors import ConnectionFailure


# client = MongoClient("192.168.5.167", 27017, serverSelectionTimeoutMS=1000)
client = MongoClient("127.0.0.1", 27017, serverSelectionTimeoutMS=1000)

def is_mongo_running():
    try:
        # 发送 ping 命令来测试连接
        client.admin.command('ping')
        return True
    except ConnectionFailure:
        return False

def start_service_windows(service_name):
    while  True:
        if is_mongo_running():
            print("MongoDB 服务已启动")
        else:
            try:
                # 使用 net start 启动服务
                os.system(f"net start {service_name}")
                print(f"服务 {service_name} 已启动")
            except Exception as e:
                print(f"启动服务失败: {e}")

# 启动服务示例

start_service_windows('MongoDB')

# os.system(f"net stop MongoDB")
# os.system(f"net start MongoDB")
