import json
import random
import time

from lxml import etree
from redis import Redis
import requests

from config import checkconfig

session=requests.session()
config = checkconfig("bendi")

def demo():
    local_VQ_conn = Redis("192.168.5.%s" % config["uAddr"][0],config["uAddr"][1],config["uAddr"][2],config["uAddr"][3],socket_connect_timeout=1155)
    res = local_VQ_conn.lpop("testCookie")
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
                "traceId": str(_t - 3),

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


    #
    def Jurperson(hgid, cgid):
        url = "https://capi.tianyancha.com/cloud-operating-risk/operating/equity/getHumanEquityInfoList.json"
        params = {
            "_": str(int(time.time() * 1000)),
            "hgid": hgid,
            "cgid": cgid,
            "pageSize": "10",
            "pageNum": "1",
            "state": "-100"
        }
        response = session.get(url, headers=headers, params=params)
        print(response.text)
        print(response)

    #股东 法人  企业关联
    def asshareholder(hgid, cgid):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
        }
        cookies = {
            "auth_token": Request["token"],
            "CUID": Request["cookie_dict"]["CUID"],
            "TYCID": Request["cookie_dict"]["TYCID"],
        }
        url = f"https://www.tianyancha.com/human/{hgid}-c{cgid}"
        response = requests.get(url, headers=headers,cookies=cookies)
        html = etree.HTML(response.text)
        with open("1.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print(response.text)
        json_date = json.loads(html.xpath('//script[@id="__NEXT_DATA__"]/text()')[0])
        #股东数据
        gudonginfo = json_date["props"]["pageProps"]["dehydratedState"]["queries"][7]["state"]["data"]["data"]["holderList"]
        #法人数据
        legalinfo=json_date["props"]["pageProps"]["dehydratedState"]["queries"][7]["state"]["data"]["data"]["legalList"]
        print(gudonginfo)
        print(legalinfo)

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
    print(response.text)
    datas=response.json()["data"]
    items=datas["holder"]["items"]
    for idex,item in enumerate(items):
        name=item["name"]
        print(name)
        "1984012283"
        hgid=str(item['hgid'])
        "22822"
        cid=str(item["cid"])
        Jurperson(hgid, cid)
        print("*"*100)
        asshareholder(hgid, cid)
        print("*" * 100)
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

# demo()

def demo1():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
    }
    cookies = {
        "CUID": "41bdd4821eb128a557afdc7d89d1d4b7",
        "TYCID": "52c328c0fb2811ef84627f9b3373dbc7",
        "auth_token": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxODgwNjI3Mzk4MCIsImlhdCI6MTc0Mjk3NDMxNiwiZXhwIjoxNzQ1NTY2MzE2fQ.ylvDFK8RPatLyoE7eY5iGh6OESOhoA3d6-2sm1qHxfSiDs7lwdyW6oVsDxAfwXB8dYVELhXa07AOo2Y_bGBF6A	",
    }
    url = "https://www.tianyancha.com/human/2277807374-c150041670"
    response = requests.get(url, headers=headers, cookies=cookies)
    html = etree.HTML(response.text)
    json_date = json.loads(html.xpath('//script[@id="__NEXT_DATA__"]/text()')[0])
    gudong = json_date["props"]["pageProps"]["dehydratedState"]["queries"][7]["state"]["data"]["data"]["holderList"]
    faren = json_date["props"]["pageProps"]["dehydratedState"]["queries"][7]["state"]["data"]["data"]["legalList"]
    print(gudong)
    print("\n"+"*"*100+"\n")
    print(faren)


# demo1()

def demo2():
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "DNT": "1",
        "Origin": "https://www.tianyancha.com",
        "Pragma": "no-cache",
        "Referer": "https://www.tianyancha.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "X-AUTH-TOKEN": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNzc3MzE2NDMyNiIsImlhdCI6MTc0NDc2NTA2MiwiZXhwIjoxNzQ3MzU3MDYyfQ.AGv-n-ChTCzl1cQC_0KmoAgHKgJbdAYY4L-pzs3SqpUfY_hgs2fIkz_xZJS_02_kgEVuxkeLvbMImli-lC7Vcw",
        "X-TYCID": "e5010c901a5c11f08e6c972720f5b8d7",
        "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }
    url = "https://capi.tianyancha.com/cloud-company-background/companyV2/dim/historyHolder"
    params = {
        "_": "1744765211071"
    }
    data = {
        "gid": "22822",
        "pageSize": 50,
        "pageNum": 1,
        "historyType": 2,
        "benefitSharesType": 1,
        "_unUseParam": 1,
        "percentLevel": "-100",
        "keyword": ""
    }
    data = json.dumps(data, separators=(',', ':'))
    response = requests.post(url, headers=headers, params=params, data=data)

    print(response.text)
    print(response)


demo2()












