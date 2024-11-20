"""
@FileName：PikaUse.py
@Description：
@Author：18k
@Time：2024/6/14 17:15
@Department：部门
@Website：站点
@Copyright：©2019-2024 职业
:return:
"""
import json
import pika
import pymongo
from loguru import logger
from numpy import log
from retrying import retry

client = pymongo.MongoClient(host='192.168.5.167', port=27017)
collection = client["fail_MQ"]["fail_MQ_company"]
collection_1 = client["fail_MQ"]["fail_MQ_company_with"]
collection_2 = client["fail_MQ"]["fail_MQ_qualification"]
collection_3 = client["fail_MQ"]["fail_MQ_judicial"]
collection_4 = client["fail_MQ"]["fail_MQ_property"]
collection_5 = client["fail_MQ"]["fail_MQ_licence"]
collection_6 = client["fail_MQ"]["fail_MQ_certificate"]


@retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))
def consume(self, callback):
    """Start consuming AMQP messages in the current process"""
    if self.connection.is_closed:
        self.reconnect()
    try:
        channel, queue = self.setListener(callback)
        channel.start_consuming()
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        log.exception('Failed to prepare AMQP consumer')
        raise

#当时忘记发布也进行连接重连设置了，导致问题没有彻底解决。
@retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))
def publish(self, body, block=True, timeout=None, properties=None):
    pass

credentials = pika.PlainCredentials('user','user123')  # 用户名和密码
parameters = pika.ConnectionParameters(host='139.9.70.234',
            # RabbitMQ服务器地址
            port=5672,
            # RabbitMQ服务器端口，默认是5672
            virtual_host='/',
            # 虚拟主机，默认是'/'
            credentials=credentials,
            # 用户名和密码
            socket_timeout=10,
            heartbeat=0,
            retry_delay=10,
            connection_attempts=10
)
# 创建一个到RabbitMQ服务器的连接
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channe2 = connection.channel()
channe3 = connection.channel()
channe4 = connection.channel()
channe5 = connection.channel()
channe6 = connection.channel()
channe7 = connection.channel()

# 创建一个队列，如果不存在的话
channel.queue_declare(queue='qqbx.dc.company',durable=True)
channe2.queue_declare(queue='qqbx.dc.industry',durable=True)
channe3.queue_declare(queue='qqbx.dc.qualification',durable=True)
channe4.queue_declare(queue='qqbx.dc.judicial',durable=True)
channe5.queue_declare(queue='qqbx.dc.property',durable=True)
channe6.queue_declare(queue='qqbx.dc.licence',durable=True)
channe7.queue_declare(queue='qqbx.dc.certificate',durable=True)

def mongoToMQ(flg,item_info):
    if flg == 0:
        try:
            # 公司详情
            channel.basic_publish(exchange='',
                    routing_key='qqbx.dc.company',
                    body=json.dumps(item_info))
            logger.success(f"company 公司数据 {item_info} 发送成功！！")
        except Exception as e:
            collection.insert_one(item_info)
    elif flg==1:
        try:
            #关联表
            channe2.basic_publish(exchange='',
                    routing_key='qqbx.dc.industry',
                    body=json.dumps(item_info))
            logger.success(f"industry 资质数据 {item_info} 发送成功！！")
        except Exception as e:
            collection_1.insert_one(item_info)
    elif flg==2:
        try:
            # 科创
            channe3.basic_publish(exchange='',
                    routing_key='qqbx.dc.qualification',
                    body=json.dumps(item_info))
            logger.success(f"qualification 科创数据 {item_info} 发送成功！！")
        except Exception as e:
            collection_2.insert_one(item_info)
    elif flg==3:
        try:
            #司法
            channe4.basic_publish(exchange='',routing_key='qqbx.dc.judicial',body=json.dumps(item_info))
            logger.success(f"judicial 司法数据 {item_info} 发送成功！！")
        except Exception as e:
            logger.error(e)
            collection_3.insert_one(item_info)
    elif flg == 4:
        try:
            #flg =4  专利
            logger.info(item_info)
            channe5.basic_publish(exchange='',
                    routing_key='qqbx.dc.property',
                    body=json.dumps(item_info))
            logger.success(f"property 专利数据 {item_info} 发送成功！！")
        except Exception as e:
            collection_4.insert_one(item_info)
    elif flg == 5:
        try:
            #flg =5  许可证
            logger.info(item_info)
            channe6.basic_publish(exchange='',
                    routing_key='qqbx.dc.licence',
                    body=json.dumps(item_info))
            logger.success(f"licence 许可证数据 {item_info} 发送成功！！")
        except Exception as e:
            collection_5.insert_one(item_info)
    else :
        try:
            # 6  资质证书
            logger.info(item_info)
            channe7.basic_publish(exchange='',
                    routing_key='qqbx.dc.certificate',
                    body=json.dumps(item_info))
            logger.success(f"certificate 资质证书 数据 {item_info} 发送成功！！")
        except Exception as e:
            collection_6.insert_one(item_info)
    connection.close()



