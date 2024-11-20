# _*_ coding:UTF-8 _*
import json
import redis

conn = redis.Redis(host='139.9.70.234', port=6379, db=6, password="anbo123", socket_connect_timeout=2000)

res=open("C:\\Users\Administrator\Desktop\processed_山东.json",encoding="utf-8").read()
for i in json.loads(res):
    print(i)
    conn.lpush("补id:补companyID",json.dumps(i))
