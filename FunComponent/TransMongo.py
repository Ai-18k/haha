# _*_ coding:UTF-8 _*
import json
import time
from concurrent.futures import ThreadPoolExecutor
from redis.client import Redis


# 超过100w数据
def read_mongoDate():
    from pymongo import MongoClient
    client = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",authSource="admin")
    cli = client["backups"]["company_list_id_name"]
    # cli = client["fujian"]["company_list_id_name"]
    cli_1 = client["fujian"]["company_id"]
    pageSize = 100
    currentPage=187
    while True:
        for i in cli.find({}, {"_id": False}).skip((currentPage - 1) * pageSize).limit(pageSize):
            print(i)
            # aa = dict()
            # if "areaCode" in i:
            #     aa["province"]=i["province"]
            #     aa["city"]=i["city"]
            #     aa["areaCode"]=i["areaCode"]
            #     aa["briefName"]=i["briefName"]
            #     aa["base"]=i["base"]
            #     aa["new_day"]=i["new_day"]
            #     aa["next_day"]=i["next_day"]
            #     aa["new_date"]=i["new_date"]
            #     aa["next_day"]=i["next_day"]
            #     aa["company"]=i["company"]
            #     aa["id"]=i["id"]
            # else:
            #     aa["company"] = i["company"]
            #     aa["id"] = i["id"]
            if i["company"] == "福州锦孝和贸易有限公司":
                cli_1.insert_one(i)
                print("--------------------------结束！----------------------------")
                break
            else:
                cli_1.insert_one(i)
        currentPage+=1
        print(">>>>>>>>>>>>>>>>>>>>>>>",currentPage)
        if currentPage >=6091:
            break




#100w数据以下
from pymongo import MongoClient
# client = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",
#                          authSource="admin")


client = MongoClient(host='192.168.5.167', port=27017)

keys=["new_add_company_id","new_add_company_id_01"]
cli = client["hubei"]["company"]

def cp_mongoDate():
    _=1
    with ThreadPoolExecutor(max_workers=5) as f:
        for key in keys:
            cli = client["fujian"][key]
            data = list(cli.find())
            futures = []
            for i in data:
                print(i)
                if "_id" in i:
                    del i["_id"]
                futures.append(f.submit(save,data=i))
                _ += 1
                print("..................第 %d 数据" % _)
                if len(futures)>=100:
                    for future in futures:
                        try:
                            future.result()
                        except Exception as e:
                            time.sleep(1)
                            print(e)
                            future.result()
                    futures.clear()
        try:
            future.result()
        except Exception as e:
            time.sleep(1)
            print(e)
            future.result()
    client.close()

def save(data):
    try:
        cli.insert_one(data)
    except Exception as e:
        print(e)
        cli.insert_one(data)
        print("保存成功")

# read_mongoDate()
# cp_mongoDate()

def mongoToRedis():

    from redis import Redis
    local_conn = Redis(host='192.168.5.177', port=8490, db=0, password="#Tn=EP(q%{", socket_connect_timeout=1170)

    def save(company):
        # local_conn.sadd("shandong:filter:company_id", company["company"])
        print(company)
        local_conn.sadd("hubei:filter:company_id", company)
        # local_conn.sadd("hubei:filter:company", company["company"])

    with ThreadPoolExecutor(max_workers=5) as f:
        pageSize=1000
        futures=[]
        _ = 0
        # for currentPage in range(3690,38000):
        for currentPage in range(2532,56000):
            data = cli.find({}, {"_id": False}).skip((currentPage - 1) * pageSize).limit(pageSize)
            for company in data:
                if "_id" in company:
                    del company["_id"]
                print(company["keys"][2])
                futures.append(f.submit(save,company=company["keys"][2]))
                _+=1
                print("......................第: ",_)
                if len(futures)>=30:
                    for future in futures:
                        try:
                            future.result()
                        except Exception as e:
                            time.sleep(1)
                            future.result()
                            print(e)
                    futures.clear()
        for future in futures:
            try:
                future.result()
            except Exception as e:
                time.sleep(1)
                future.result()
                print(e)
            #     break
            # break

# mongoToRedis()

def cityarealist():
    import requests
    local_conn = Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=170)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "DNT": "1.txt",
        "Origin": "https://www.tianyancha.com",
        "Pragma": "no-cache",
        "Referer": "https://www.tianyancha.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "X-AUTH-TOKEN": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzI5MTE0MDkxNiIsImlhdCI6MTcyNjMxNjQ5MywiZXhwIjoxNzI4OTA4NDkzfQ.uf9gfLyn01q3ECHSS5x6k8rvj7htnP2M-BOcH-J4prEmGfUboWv65bNaOlWlyeObe9f4xPeb88HhrDwszsrxyw",
        "X-TYCID": "c0bb8cd05d2311efa9578f23efc881ed",
        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }
    url = "https://napi-huawei.tianyancha.com/next/web/city/list"
    params = {
        "_": "1726316518729"
    }
    response = requests.get(url, headers=headers, params=params)
    # print(response.json())
    for i in response.json()["data"]:
        local_conn.lpush("cityAreaID",json.dumps(i))





























