import json
from loguru import logger
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












