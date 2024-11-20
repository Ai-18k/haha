# _*_ coding:UTF-8 _*
import json

import redis

conn1 = redis.Redis(host='182.43.38.79', port=6379, db=5, password="lzh990130", socket_connect_timeout=70)
conn = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123",socket_connect_timeout=70)



aa=conn1.lrange("memeryUser",0,-1)
for i in aa:
    conn.lpush("memeryUser",i)