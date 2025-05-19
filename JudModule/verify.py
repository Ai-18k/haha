import time

import redis
from autoPass import main

local_VQ_conn = redis.Redis(host='192.168.5.181', port=7933, db=0, password="fer@nhaweif576KUG",socket_connect_timeout=1170)

while True:
    if local_VQ_conn.llen("NoMemeryCookie")>0:
        for cookie in local_VQ_conn.lrange("NoMemeryCookie",0,-1):
            headers = {
                "Host": "www.tianyancha.com",
                "Cache-Control": "max-age=0",
                "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "Upgrade-Insecure-Requests": "1",
                "DNT": "1",
                "User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Referer": "https://www.tianyancha.com/company/3449518021",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            main(cookie,headers)
    else:
        print("无cookie")
        time.sleep(2)