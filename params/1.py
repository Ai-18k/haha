# _*_ coding:UTF-8 _*
import json

import redis
import requests

conn1 = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123",socket_connect_timeout=70)

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
    "X-TYCID": "c0bb8cd05d2311efa9578f23efc881ed",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
url = "https://napi-huawei.tianyancha.com/next/web/city/list"
params = {
    "_": "1726332248096"
}
response = requests.get(url, headers=headers, params=params)

for i in response.json()["data"]:
    print(i)
    conn1.lpush("cityAreaID",json.dumps(i))



