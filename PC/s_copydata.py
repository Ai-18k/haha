from pymongo import MongoClient, WriteConcern,errors
from concurrent.futures import ThreadPoolExecutor,as_completed

from pymongo.errors import ConnectionFailure

class A:
    write_concern = WriteConcern(w=1)
    source_client = MongoClient(host='192.168.5.167', port=27017)
    target_client = MongoClient(host='192.168.5.101', port=27017)

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
                new_collection.with_options(write_concern=self.write_concern).insert_many(docs,bypass_document_validation=True)
                            #,bypass_document_validation=True,ordered=False)
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
            with ThreadPoolExecutor(max_workers=6) as f:
                for db_name in source_dbs:
                    if not db_name.startswith((
                    "CCDate", "CCDate_id",'CheckGaps','TYCDate', 'admin', 'config', 'filter','local', 'property', 'sfaj', "judicial",
                                              # "anhui",
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
                                # "商标信息",
                                # "资质证书",
                                # "作品著作权",
                                # "行政许可",
                                # "软著著作权",
                                # "company",
                                # "company_qualification",
                                # "company_with",
                                # "sfaj",
                                # "sifa",
                                # "zlxx",
                                # "法院公告",
                                # "股权冻结",
                                # "经营异常",
                                # "限制消费",
                                # "失信被执行人",
                                # "行政处罚",
                                # "裁判文书",
                                # "被执行人",
                                # "历史被执行人",
                                # "历史裁判文书",
                                # "历史法院公告",
                                # "历史股权冻结",
                                # "历史经营异常",
                                # "历史失信被执行人",
                                # "历史限制消费",
                                # "历史行政处罚",
                                "filter_comp","filter_company_id","filter_cpws_com","filter_dxxk","filter_h_cpws_com","filter_params","filter_gudong","filter_zzzs",
                                "filter_params1","filter_rzzzq","filter_sbxx","filter_sfaj","filter_xzxk","filter_zlxx_com","filter_zpzzq","filter_zzzs"
                                "fail_商标信息", "fail_电信许可", "fail_历史sifa_companyid", "fail_软著著作权","fail_company_id",
                                "fail_行政许可", "fail_资质证书", "fail_作品著作权",
                                "fails_商标信息", "fails_电信许可", "fails_历史sifa_companyid", "fails_软著著作权","fails_company_id",
                                "fails_行政许可", "fails_资质证书", "fails_作品著作权",
                                 "fails_历史行政处罚","fails_历史限制消费","fails_历史失信被执行人","fails_历史经营异常","fails_历史股权冻结","fails_历史法院公告",
                                "fails_历史裁判文书","fails_历史被执行人",
                                "fail_judicial_with","fail_property_with", "fail_sifa_companyid", "fail_地区时间参数", "公司详情失败公司id"]:
                                print(f"{collection_name}:已经完成迁移！！")
                            else:
                                print(f"复制集合: {collection_name}")
                                threads.append(f.submit(self.copy_collection,db_name=db_name, collection_name=collection_name))
                for thread in as_completed(threads):
                    thread.result()

        except ConnectionFailure:
            print("无法连接到 MongoDB 服务器。请检查网络连接。")
        except Exception as e:
            print(f"出现错误: {e}")


A().copy_mongo_multithreaded()
