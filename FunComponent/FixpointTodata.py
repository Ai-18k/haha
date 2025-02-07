import json
from concurrent.futures import ThreadPoolExecutor
import pika
import pymongo
import redis
from loguru import logger


class SendMQ:

    def __init__(self,key1,key2,num):
        self.client = pymongo.MongoClient(host='192.168.5.167', port=27017)
        self.local_conn=redis.Redis(host='192.168.5.167', port=10824, password="e8Mzr}$%jsuCxKn4r#mm",db=0,decode_responses=True)
        self.coll = self.client[key1][key2]
        self.coll1 = self.client[key1][key2]
        self.coll2 = self.client[key1]["MQfail"]
        self.pageSize = num
        self.company_list=[]


    def mongoToMQ(self,flg,item_info):
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
                channel.basic_publish(exchange='',routing_key='qqbx.dc.company', body=json.dumps(item_info))
                logger.success(f"【* qqbx.dc.company】发送成功:{item_info}!!")
            except Exception as e:
                logger.error(e)
                self.coll2.insert_one(item_info)
        elif flg == 2:
            try:
                channe2.basic_publish(exchange='',
                                      routing_key='qqbx.dc.industry', body=json.dumps(item_info))
                logger.success(f"【*qqbx.dc.industry】发送成功:{item_info}!!")
            except Exception as e:
                logger.error(e)
                self.coll2.insert_one(item_info)
        elif flg == 3:
            try:
                channe3.basic_publish(exchange='', routing_key='qqbx.dc.qualification', body=json.dumps(item_info))
                logger.success(f"【*qqbx.dc.qualification】发送成功:{item_info} 发送成功！！")
            except Exception as e:
                logger.error(e)
                self.coll2.insert_one(item_info)
        elif flg == 4:
            try:
                # 司法
                logger.info(item_info)
                channe4.basic_publish(exchange='', routing_key='qqbx.dc.judicial', body=json.dumps(item_info))
                logger.success(f"judicial 司法数据 {item_info} 发送成功！！")
            except Exception as e:
                logger.error(e)
                self.coll2.insert_one(item_info)
        else:
            try:
                # flg =5 专利
                logger.info(item_info)
                channe5.basic_publish(exchange='',
                                      routing_key='qqbx.dc.property', body=json.dumps(item_info))
                logger.success(f"property 专利数据 {item_info} 发送成功！！")
            except Exception as e:
                logger.error(e)
                self.coll2.insert_one(item_info)
        connection.close()


    def demo(self,item):
        try:
            logger.info(f"keys是否存在:{'keys' in item}")
            if 'keys' in item:
                item_info = item["keys"]
                # logger.info(item_info)
                if item_info is None:
                    return
                # try:
                #     logger.info(item_info[2])
                #     # collection_5_1.insert_one({'company': item_info[2]})
                #     # collection_5.insert_one({"data":item_info})
                #     logger.success("数据插入成功！")
                # except pymongo.errors.DuplicateKeyError:
                #     logger.error("数据已存在，插入失败！")
                if len(item_info) == 29 or 31:
                    # self.local_conn.sadd("shandong:filter:company", item_info[2])
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
                    # self.local_conn.sadd("filter:serv_company", item_info[3])
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
                self.company_list.append(data)
            else:
                with open("异常数据.json", "a", encoding="utf-8") as f:
                    f.write(item)

        except Exception as e:
            logger.error(e)
            if "_id" in item:
                del item["_id"]
            collection_7.insert_one(item)

    def send(self,currentPage):
        with ThreadPoolExecutor(3) as f:
            company_list = list()
            # for item in resules[page * 20:(page + 1) * 20]:
            data = self.coll.find({}, {"_id": False}).skip((currentPage - 1) * self.pageSize).limit(self.pageSize)
            _ = 0
            futures=[]
            for item in data:
                # print(item)
                futures.append(f.submit(self.demo, item=item))
                _ += 1

        logger.info(company_list)
        logger.info(len(company_list))
        self.mongoToMQ(1, company_list)
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
    def localMongoToMQ(self):
        self.coll.count_documents()
        with ThreadPoolExecutor(3) as f:
            # send(1)
            futures = []
            for i in range(1, 50000):
                futures.append(f.submit(self.send, currentPage=i))
                logger.info(f"第 {i} 页数据")
                # break
                if len(futures) >= 100:
                    for future in futures:
                        future.result()
                    futures.clear()
            for future in futures:
                future.result()


if __name__ == '__main__':
    key1="zhejiang"
    key2="sorcomp"
    SendMQ(key1,key2,100).localMongoToMQ()







