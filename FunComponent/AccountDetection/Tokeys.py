import redis
import json


conn = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123",socket_connect_timeout=1170)
local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=1170)
local_VQ_conn = redis.Redis(host='192.168.5.181', port=10281, db=0, password="*s,8<[VVS6h.nnWZ=cv{",
								 socket_connect_timeout=1170)

def demo():

	for _ in range(30):
		# res=local_VQ_conn.lpop("memeryUser")
		res=local_VQ_conn.lpop("searchMobil")
		# res=local_VQ_conn.lpop("sifaUser")
		# res=local_VQ_conn.lrange("memeryUser",0,-1)
		# res=local_VQ_conn.lrange("searchMobil",0,-1)
		# res=local_VQ_conn.lrange("sifaUser",0,-1)
		print(json.loads(res))
		local_VQ_conn.lpush("sifaUser",res)
		# local_VQ_conn.lpush("totleUser", res)

		#
		# for i in res:
		# 	print(json.loads(i))
		# 	local_VQ_conn.lpush("searchMobil",i)


if __name__ == '__main__':
	demo()
