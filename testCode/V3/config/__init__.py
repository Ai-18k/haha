import json
import threading

from curl_cffi import requests
from loguru import logger
from pymongo import MongoClient, WriteConcern, ASCENDING
from redis.client import Redis

def checkconfig(area):
    with open("config.json", "r", encoding="utf-8") as file:
        config = file.read()
    config = json.loads(config)
    serv_conn =Redis('139.9.70.234', 6379,2, "anbo123", socket_connect_timeout=170)
    addr=serv_conn.get(area)
    config["servSAddr"]=json.loads(serv_conn.get("servSAddr").decode("utf-8"))
    config["localSAddr"]=json.loads(serv_conn.get("localSAddr").decode("utf-8"))
    addr = json.loads(addr.decode())
    config["fAddr"]=addr
    if 'localSAddr' not in config:
        logger.error("请设置数据保存地址！！")
        raise "未设置文件保存地址"
    else:
        if len(config['localSAddr'])<2:
            logger.error("请 正确配置 数据保存地址！！")
            raise "未正确配文件保存地址"
    if not serv_conn.exists(area):
        logger.error("未找到与之相关的设备信息，请检查名称或者检查设备是否存在")
        raise "名称有误或者设备不存在，请检查！！"
    config["uAddr"]=json.loads(serv_conn.get("bendi"))
    config["rkey"]=area
    config["area"]=area
    _isproxy=json.loads(serv_conn.get("proxy:_isUse").decode("utf-8"))
    if _isproxy["isUse"]:
        config["proxy"]=_isproxy["info"]
    else:
        config["proxy"]=False
    return config

class Config(object):

    def __init__(self, area):
        self.config = checkconfig(area)
        self.session = requests.Session()
        self.local_conn = Redis("192.168.5.%s" % self.config["fAddr"][0],
                                self.config["fAddr"][1],
                                self.config["fAddr"][2],
                                self.config["fAddr"][3],
                                socket_connect_timeout=1170)
        self.conn = Redis("192.168.5.%s" % self.config["uAddr"][0],
                                   self.config["uAddr"][1],
                                   self.config["uAddr"][2],
                                   self.config["uAddr"][3],
                                   socket_connect_timeout=1155)
        self.client_01 = MongoClient(host="139.9.70.%s" % self.config["servSAddr"][0],
                                     port=self.config["servSAddr"][1],
                                     username=self.config["servSAddr"][2],
                                     password=self.config["servSAddr"][3],
                                     authSource=self.config["servSAddr"][4])
        self.client = MongoClient("192.168.5.%s" % self.config['localSAddr'][0],
                                  self.config['localSAddr'][1])
        self.cli_5 = self.client[self.config["rkey"]]["company_id"]
        self.db = self.client[area]["sorcomp"]
        self.gd = self.client[area]["gudong"]
        self.kpa = self.client[area]["gudong_kpa"]
        self.sif = self.client[area]["gudong_sif"]
        self.gudong_filter_key = area + ":filter:gudong"
        self.filter_key1 = area + ":filter:gdcomp"
        self.comp_key = area + ":gudongList"
        self.write_concern = WriteConcern(w=1)

        # 资质证书类
        self.cli=self.client[self.config["rkey"]]['商标信息']
        self.cli1=self.client[self.config["rkey"]]['作品著作权']
        self.cli2=self.client[self.config["rkey"]]['电信许可']
        self.cli3=self.client[self.config["rkey"]]['软著著作权']
        self.cli4=self.client[self.config["rkey"]]['行政许可']
        self.cli5=self.client[self.config["rkey"]]['资质证书']
        self.c_fail = self.client[self.config["rkey"]]["fails_商标信息"]
        # self.c_fail.create_index([('company', ASCENDING)], unique=True)
        self.c_fail1 = self.client[self.config["rkey"]]["fails_作品著作权"]
        self.c_fail1.create_index([('company', ASCENDING)], unique=True)
        self.c_fail2 = self.client[self.config["rkey"]]["fails_电信许可"]
        # self.c_fail2.create_index([('company', ASCENDING)], unique=True)
        self.c_fail3 = self.client[self.config["rkey"]]["fails_软著著作权"]
        # self.c_fail3.create_index([('company', ASCENDING)], unique=True)
        self.c_fail4 = self.client[self.config["rkey"]]["fails_行政许可"]
        # self.c_fail4.create_index([('company', ASCENDING)], unique=True)
        self.c_fail5 = self.client[self.config["rkey"]]["fails_资质证书"]
        # self.c_fail5.create_index([('company', ASCENDING)], unique=True)
        self.sbxx_list=set()   #4
        self.zpzzq_list=set() #5
        self.rzzzq_list=set()  #6
        self.f_map = {"4": self.sbxx_list, "5": self.zpzzq_list,"6": self.rzzzq_list}
        self.zi_area_key = self.config["rkey"] + ":company_id"
        self.sbxx_filter_key = self.config["rkey"] + ":filter:sbxx"
        self.zpzzq_filter_key = self.config["rkey"] + ":filter:zpzzq"
        self.rzzzq_filter_key = self.config["rkey"] + ":filter:rzzzq"
        self.zzzs_filter_key = self.config["rkey"] + ":filter:zzzs"
        self.xzxk_filter_key = self.config["rkey"] + ":filter:xzxk"
        self.dxxk_filter_key = self.config["rkey"] + ":filter:dxxk"
        self.thread_local = threading.local()

        # 历史司法数据
        self.fy_coll= self.client[self.config["rkey"]]["历史法院公告"]
        self.jy_coll = self.client[self.config["rkey"]]["历史经营异常"]
        self.xx_coll = self.client[self.config["rkey"]]["历史限制消费"]
        self.cs_coll = self.client[self.config["rkey"]]["历史裁判文书"]
        self.bzx_coll = self.client[self.config["rkey"]]["历史被执行人"]
        self.xxzx_coll = self.client[self.config["rkey"]]["历史失信被执行人"]
        self.xc_coll = self.client[self.config["rkey"]]["历史行政处罚"]
        self.gd_coll = self.client[self.config["rkey"]]["历史股权冻结"]
        self.f_fy_coll = self.client[self.config["rkey"]]["fails_历史法院公告"]
        # self.col.create_index([('company', ASCENDING)], unique=True)
        self.f_jy_coll = self.client[self.config["rkey"]]["fails_历史经营异常"]
        # self.col1.create_index([('company', ASCENDING)], unique=True)
        self.f_xx_coll = self.client[self.config["rkey"]]["fails_历史限制消费"]
        # self.col2.create_index([('company', ASCENDING)], unique=True)
        self.f_cs_coll = self.client[self.config["rkey"]]["fails_历史裁判文书"]
        # self.col3.create_index([('company', ASCENDING)], unique=True)
        self.f_bzx_coll = self.client[self.config["rkey"]]["fails_历史被执行人"]
        # self.col4.create_index([('company', ASCENDING)], unique=True)
        self.f_xxzx_coll = self.client[self.config["rkey"]]["fails_历史失信被执行人"]
        # self.col5.create_index([('company', ASCENDING)], unique=True)
        self.f_xc_coll = self.client[self.config["rkey"]]["fails_历史行政处罚"]
        # self.col6.create_index([('company', ASCENDING)], unique=True)
        self.f_gd_coll = self.client[self.config["rkey"]]["fails_历史股权冻结"]
        # self.col7.create_index([('company', ASCENDING)], unique=True)
        self.hsf_filter_key = self.config["rkey"] + ":filter:h_cpws_com"
        self.hsf_area_key = self.config["rkey"] + ":company_id_04"

        # 现在的司法裁判数据
        # self.coll_2 = self.client_01[self.config["rkey"]]["法院公告"]
        # self.coll_3 = self.client_01[self.config["rkey"]]["经营异常"]
        # self.coll_4 = self.client_01[self.config["rkey"]]["限制消费"]
        # self.coll_5 = self.client_01[self.config["rkey"]]["裁判文书"]
        # self.coll_6 = self.client_01[self.config["rkey"]]["被执行人"]
        # self.coll_7 = self.client_01[self.config["rkey"]]["失信被执行人"]
        # self.coll_8 = self.client_01[self.config["rkey"]]["行政处罚"]
        # self.coll_9 = self.client_01[self.config["rkey"]]["股权冻结"]
        self.nfy_coll = self.client[self.config["rkey"]]["法院公告"]
        self.njy_coll = self.client[self.config["rkey"]]["经营异常"]
        self.nxf_coll = self.client[self.config["rkey"]]["限制消费"]
        self.ncp_coll = self.client[self.config["rkey"]]["裁判文书"]
        self.nzx_coll = self.client[self.config["rkey"]]["被执行人"]
        self.nszx_coll = self.client[self.config["rkey"]]["失信被执行人"]
        self.nxz_coll = self.client[self.config["rkey"]]["行政处罚"]
        self.ngq_coll = self.client[self.config["rkey"]]["股权冻结"]

        self.f_nfy_coll = self.client[self.config["rkey"]]["fails_法院公告"]
        self.f_nfy_coll.create_index([('company', ASCENDING)], unique=True)

        self.f_njy_coll = self.client[self.config["rkey"]]["fails_经营异常"]
        self.f_njy_coll.create_index([('company', ASCENDING)], unique=True)

        self.f_nxf_coll = self.client[self.config["rkey"]]["fails_限制消费"]
        self.f_nxf_coll.create_index([('company', ASCENDING)], unique=True)

        self.f_ncp_coll = self.client[self.config["rkey"]]["fails_裁判文书"]
        self.f_ncp_coll.create_index([('company', ASCENDING)], unique=True)

        self.f_nzx_coll = self.client[self.config["rkey"]]["fails_被执行人"]
        self.f_nzx_coll.create_index([('company',ASCENDING)], unique=True)

        self.f_nszx_coll = self.client[self.config["rkey"]]["fails_失信被执行人"]
        self.f_nszx_coll.create_index([('company', ASCENDING)], unique=True)

        self.f_nxz_coll = self.client[self.config["rkey"]]["fails_行政处罚"]
        self.f_nxz_coll.create_index([('company', ASCENDING)], unique=True)

        self.f_ngq_coll = self.client[self.config["rkey"]]["fails_股权冻结"]
        self.f_ngq_coll.create_index([('company',ASCENDING)], unique=True)

        self.nsc_area_key = self.config["rkey"] + ":company_id_02"
        self.nsc_filter_key = self.config["rkey"] + ":filter:cpws_com"


        # 司法专利类
        self.cli_5 = self.client[self.config["rkey"]]["company_id"]
        self.cli = self.client[self.config["rkey"]]["sfaj"]
        self.cli_1 = self.client[self.config["rkey"]]["zlxx"]
        # self.coll_2 = self.client_01[self.config["rkey"]]["司法案件"]
        # self.coll_3 = self.client_01[self.config["rkey"]]["专利"]
        self.coll_2_1 = self.client[self.config["rkey"]]["fails_司法案件"]
        self.coll_2_1.create_index([("company", ASCENDING)], unique=True)
        self.coll_3_1 = self.client[self.config["rkey"]]["fails_专利"]
        self.coll_3_1.create_index([("company", ASCENDING)], unique=True)
        self.sfaj_item = list()
        self.zlxx_item = list()
        self.sifa_filter_key=self.config["rkey"]+":filter:sfaj"
        self.zlxx_filter_key=self.config["rkey"]+":filter:zlxx_com"
        self.sifa_area_key = self.config["rkey"] + ":company_id_03"

        self.gudong_item=list()

