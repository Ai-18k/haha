from pymongo import MongoClient, WriteConcern
from pymongo.errors import ConnectionFailure
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
import time
from retrying import retry
import os
import subprocess
import sys
import ctypes



class A:
    write_concern = WriteConcern(w=1)
    source_client = MongoClient(host='192.168.5.167', port=27017)
    target_client = MongoClient(host='192.168.5.113', port=27017)
    

    # 判断是否以管理员身份运行
    def is_admin(self):
        try:
            return (sys.platform == "win32" and ctypes.windll.shell32.IsUserAnAdmin() != 0)
        except:
            return False


    # 提升为管理员权限并执行命令
    def run_as_admin(self,command):
        while  True:
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
                        subprocess.run(f'powershell -Command "Start-Process cmd.exe -ArgumentList \'/c net start {command}\' -Credential (New-Object System.Management.Automation.PSCredential(\'anbo\', (ConvertTo-SecureString \'anbo1234\' -AsPlainText -Force)))"', shell=True)
                        print(f"服务 {command} 已启动")
                    except Exception as e:
                        print(f"启动服务失败: {e}")
                       
                       
    def is_mongo_running(self):
        try:
            # 发送 ping 命令来测试连接
            self.target_client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False


    # def start_service_windows(self,service_name):
        # while  True:
            # if self.is_mongo_running():
                # print("MongoDB 服务已启动")
                # return True
            # else:
                # try:
                    # # 使用 net start 启动服务
                    # os.system(f"net start {service_name}")
                    # print(f"服务 {service_name} 已启动")
                # except Exception as e:
                    # print(f"启动服务失败: {e}")
                    
    #@retry(wait_fixed=1000)
    def copy_collection(self, db_name, collection_name):
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
            total_copied = 0

            while True:
                query = {}
                if last_id:
                    query["_id"] = {"$gt": last_id}  # 基于 _id 分页
                docs_cursor = old_collection.find(query).sort("_id", 1).limit(pageSize)
                docs = list(docs_cursor)

                if not docs:  # 如果没有数据，退出循环
                    print(f"{db_name}.{collection_name} 没有更多数据需要复制。")
                    break

                # 批量插入数据到目标集合
                new_collection.with_options(write_concern=self.write_concern).insert_many(docs)
                total_copied += len(docs)

                # 打印进度
                print(f"成功复制 {(currentPage + 1) * pageSize} 条数据到 {db_name}.{collection_name}")
                
                # 更新 last_id 和页码
                last_id = docs[-1]["_id"]
                currentPage += 1

            print(f"数据库 {db_name} 的集合 {collection_name} 完成数据复制，成功复制 {total_copied} 条记录。")
        except Exception as e:
            logger.error(f"复制 {db_name}.{collection_name} 时出现错误: {e}")
            # self.start_service_windows('MongoDB')
            self.run_as_admin('MongoDB')
            raise ConnectionFailure("链接成功")
    
    
    def copy_mongo_multithreaded(self):
        try:
            source_dbs = self.source_client.list_database_names()
            threads = []
            with ThreadPoolExecutor(max_workers=6) as f:
                for db_name in source_dbs:
                    if not db_name.startswith(("CCDate", "CCDate_id", 'CheckGaps',
                                               'TYCDate', 'admin', 'config', 'filter',
                                               'local', 'property', 'sfaj', "judicial", "test","company",
                                              "beijing",
                                              "chongqing",
                                              "fujian",
                                              "guizhou",
                                              "hainan",
                                              "hebei",
                                              "hubei",
                                              "jiangsu",
                                              #"jiangxi",
                                              "jilin",
                                              "neimenggu",
                                              "ningxia",
                                              "sanxi",
                                              "shandong",
                                              "shanghai",
                                              "shanxi",
                                              "xinjiang",
                                              "xizang",
                                              "zhejiang",
                                              "liaoning",
                                              "sichuan",
                                              "hunan",
                                              "guangxi",
                                              "anhui",    
                                              "henan",   
                                              "yunnan", 
                                              "guangdong",
                                              "heilongjiang",
                                              "qinghai",
                                              "tianjin",
                                              "gansu",
                                              "taiwan",
                                              "xianggang"
                                               )):
                        print(f"开始复制数据库: {db_name}")
                        collection_name="sorcomp"
                        threads.append(f.submit(self.copy_collection, db_name=db_name, collection_name=collection_name))
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

# 执行复制任务
A().copy_mongo_multithreaded()
