import json
import random
import time

from redis import Redis
import requests

from config import checkconfig

session=requests.session()
config = checkconfig("bendi")

def demo():
    local_VQ_conn = Redis("192.168.5.%s" % config["uAddr"][0],config["uAddr"][1],config["uAddr"][2],config["uAddr"][3],socket_connect_timeout=1155)
    res = local_VQ_conn.lpop("searchCookie")
    Request = json.loads(res.decode("utf-8"))
    print(Request)
    session.cookies = requests.utils.cookiejar_from_dict(Request["cookie_dict"])
    headers = {
        "Accept": "application/json, text/plain, */*",
        "version": "TYC-Web",
        "x-spm-referer": "https://graph.tianyancha.com/web/tree/enterprise_structure?cid=22822&category=companyStructure&depth=1&entityType=2&spm=&pm=&export=&canvasType=",
        "referrer_pm": "",
        "X-TYCID": Request["cookie_dict"]["TYCID"],
        "X-AUTH-TOKEN": Request["token"],
        "laneTag": "false",
        "Content-Type": "application/json"
    }

    url = "https://cloud-gateway.tianyancha.com/cloud-company-background/company/enterpriseMapV2"

    def offset():
        # 获取当前时间戳
        current_time = time.time()

        # 分割为整数部分和小数部分
        integer_part = int(current_time)  # 小数点之前的部分
        decimal_part = current_time - integer_part  # 小数点之后的部分

        # 整数部分乘以 1000
        integer_part_ms = integer_part * 1000

        # 小数部分保留三位并乘以 1000
        decimal_part_ms = int(round(decimal_part, 3) * 1000)

        # 随机生成一个 0 到 decimal_part_ms 之间的数
        random_offset = random.randint(0, decimal_part_ms)

        # 构造随机时间戳
        random_timestamp = integer_part_ms + random_offset
        return random_timestamp


    def pj(item):
        _t = offset()
        if "pid" in item:
            url = "https://cloud-gateway.tianyancha.com/tyc-enterprise-graph/ei/human/card"
            pid = item["pid"]
            return url,{
                "humanId": pid,
                "_": str(_t),
                "traceId": str(_t - 3)
            }
        elif "gid" in item:
            url = "https://cloud-gateway.tianyancha.com/tyc-enterprise-company-agg/ei/company/card"
            gid = item["gid"]
            return url,{
                "companyId": gid,
                "companyName": "x",
                "_": str(_t),
                "traceId": str(_t - 3)
            }
        else:
            print(item)
            return {}


    _t=offset()
    params = {
        "gid": "22822",
        # "gid": "7446792368",
        "code": "all",
        "offset": "1",
        "limit": "10",
        "_": str(_t),
        "traceId": str(_t-3)
    }
    response = session.get(url, headers=headers, params=params)
    datas=response.json()["data"]
    items=datas["holder"]["items"]
    for idex,item in enumerate(items):
        name=item["name"]
        url, params = pj(item)
        response = requests.get(url, headers=headers, params=params)
        print(response.json())
        if "baseInfoList" in response.json()["data"]:
            showText=response.json()["data"]["baseInfoList"]
            item["data"]=response.json()["data"]
            text=showText[1]["showText"]
            print(text)
            print(datas)
        else:
            print(f"****没有找到【{name}】相关的信息！！")

demo()









