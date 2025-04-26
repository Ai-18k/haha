import json
import threading
from concurrent.futures import ThreadPoolExecutor
import pika
import pymongo
from loguru import logger
from pymongo import errors
from redis import Redis
from ParseFile.detailparam import getdata
from MQitems.PikaUse import SendMQ


# 加载静态配置
with open('Vchongqing.json', 'r', encoding='utf-8') as file:
    Vqtext = json.load(file)


class UploadServ:

    def __init__(self, key1, key2, num):
        # 初始化连接
        self.serv_conn = Redis(host='127.0.0.1', port=10238, db=0, password="vi4*87taTZBel&DyWL)A",socket_connect_timeout=170)
        self.addr = json.loads(self.serv_conn.get(key1).decode('utf-8'))
        self.client = pymongo.MongoClient(host='192.168.5.167', port=27017)
        self.local_conn = Redis("192.168.5." + self.addr[0], self.addr[1], self.addr[2], self.addr[3], socket_connect_timeout=1170)
        self.coll = self.client[key1][key2]
        self.coll2 = self.client[key1]["MQfail"]
        self.coll4 = self.client[key1]["error_data"]
        self.coll4.create_index([('error_data', pymongo.ASCENDING)], unique=True, sparse=True)
        self.pageSize = num
        self.processed_ids = set()  # 处理过的公司ID集合
        self.thread_local = threading.local()

    def _send_message_to_queue(self, flg, item_info):
        """向指定队列发送消息"""
        credentials = pika.PlainCredentials('user', 'user123')
        parameters = pika.ConnectionParameters(
            host='139.9.70.234',
            port=5672,
            virtual_host='/',
            credentials=credentials,
            socket_timeout=100,
            heartbeat=300,
            retry_delay=300,
            connection_attempts=10
        )

        try:
            # 创建连接和频道
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channe2 = connection.channel()
            channe3 = connection.channel()
            channe4 = connection.channel()
            channe5 = connection.channel()

            # 创建队列
            channel.queue_declare(queue='qqbx.dc.company', durable=True)
            channe2.queue_declare(queue='qqbx.dc.industry', durable=True)
            channe3.queue_declare(queue='qqbx.dc.qualification', durable=True)
            channe4.queue_declare(queue='qqbx.dc.judicial', durable=True)
            channe5.queue_declare(queue='qqbx.dc.property', durable=True)

            # 根据flg选择发送的队列
            if flg == 1:
                self._send_to_channel(channel, item_info, "qqbx.dc.company")
            elif flg == 2:
                self._send_to_channel(channe2, item_info, "qqbx.dc.industry")
            elif flg == 3:
                self._send_to_channel(channe3, item_info, "qqbx.dc.qualification")
            elif flg == 4:
                self._send_to_channel(channe4, item_info, "qqbx.dc.judicial")
            else:
                self._send_to_channel(channe5, item_info, "qqbx.dc.property")

            connection.close()
        except Exception as e:
            logger.error(f"发送失败: {e}")
            self.coll2.insert_one(item_info)

    def _send_to_channel(self, channel, item_info, queue_name):
        """发送信息到指定的队列"""
        try:
            channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(item_info))
            logger.success(f"【* {queue_name}】发送成功: {item_info}!")
        except Exception as e:
            logger.error(f"发送失败 {queue_name}: {e}")
            self.coll2.insert_one(item_info)

    def process_item_info(self, info):
        """处理每个公司信息"""
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

            # 批量发送数据
            if len(self.thread_local.kechuang_item) >= 20:
                SendMQ().mongoToMQ(2, self.thread_local.kechuang_item)
                self.thread_local.kechuang_item.clear()

            if len(self.thread_local.data1_item) >= 20:
                SendMQ().mongoToMQ(1, self.thread_local.data1_item)
                self.thread_local.data1_item.clear()

            if len(self.thread_local.data_item) >= 20:
                SendMQ().mongoToMQ(0, self.thread_local.data_item)
                self.thread_local.data_item.clear()
        except Exception as e:
            logger.error(f"处理失败: {e}")
            try:
                self.coll4.insert_one(info)
                print("数据插入成功！")
            except errors.DuplicateKeyError:
                print("数据已存在，插入失败！")

    def send_data_to_mq(self, currentPage):
        """分页发送数据到消息队列"""
        with ThreadPoolExecutor(6) as f:
            data = self.coll.find({}, {"_id": False}).skip(currentPage * self.pageSize).limit(self.pageSize)
            futures = []
            for item in data:
                futures.append(f.submit(self.process_item_info, item))
            for future in futures:
                future.result()

        logger.success(f"第 {currentPage + 1} 页数据发送成功")

    def local_mongo_to_mq(self):
        """从本地MongoDB获取数据并发送到MQ"""
        num = self.coll.estimated_document_count()
        self.start= int(self.serv_conn.get("tis:page").decode())

        with ThreadPoolExecutor(5) as f:
            futures = []
            for i in range(self.start, num // self.pageSize + 1):
            # for i in range(self.start, 2):
                self.serv_conn.set("tis:page", i)
                futures.append(f.submit(self.send_data_to_mq, i))
                logger.info(f"第 {i} 页数据")
                if len(futures) >= 50:
                    for future in futures:
                        future.result()
                    futures.clear()
            for future in futures:
                future.result()


if __name__ == '__main__':
    key1 =  "shandong"
    key2 = "sorcomp"
    UploadServ(key1, key2, 100).local_mongo_to_mq()






