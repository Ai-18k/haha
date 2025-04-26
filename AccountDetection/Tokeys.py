from concurrent.futures import ThreadPoolExecutor
from bson import ObjectId
import redis
import json
from config import checkconfig
from pymongo import MongoClient

config = checkconfig("bendi")

# conn = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123",socket_connect_timeout=1170)
conn = redis.Redis(host='192.168.5.172', port=15123, db=6, password="fer@nhaweif576KUG",socket_connect_timeout=1170)
local_conn = redis.Redis(host='192.168.5.167', port=10824, db=0, password="e8Mzr}$%jsuCxKn4r#mm",socket_connect_timeout=1170)
local_VQ_conn = redis.Redis(host='192.168.5.181', port=10281, db=0, password="*s,8<[VVS6h.nnWZ=cv{",socket_connect_timeout=11170)
conn1 =redis.Redis("192.168.5."+config["uAddr"][0],config["uAddr"][1],config["uAddr"][2],config["uAddr"][3],socket_connect_timeout=1155)



def demo():

	for _ in range(60):
		# res=local_VQ_conn.lpop("memeryUser")
		res=conn1.lpop("searchMobil")
		# res=conn1.lpop("LoginUser")
		# res=conn1.lpop("sifaUser")
		# res=local_VQ_conn.lrange("memeryUser",0,-1)
		# res=local_VQ_conn.lrange("searchMobil",0,-1)
		# res=local_VQ_conn.lrange("sifaUser",0,-1)
		print(json.loads(res))
		# conn.lpush("searchMobil",res)
		# conn.lpush("LoginUser",res)
		conn1.lpush("searchMobil",res)
		# local_VQ_conn.lpush("totleUser", res)

		# for i in res:
		# 	print(json.loads(i))
		# 	local_VQ_conn.lpush("searchMobil",i)

def demo1():
	for key in conn1.keys():
		print(key.decode('utf-8'))
		if key.decode('utf-8')!="cityAreaID":
			res=conn1.get(key)
			conn.set(key.decode('utf-8'),res.decode('utf-8'))
		else:
			res = conn1.lrange(key,0,-1)
			for i in res:
				print(i.decode('utf-8'))
				conn.lpush(key.decode('utf-8'), i.decode('utf-8'))

def demo2():
	with ThreadPoolExecutor(6) as workers:
		def copy(items):
			for item in items:
				info=dict()
				info["company"]=item["name"]
				if "id" in item:
					info["id"]=item["id"]
					print(info)
					if local_VQ_conn.sismember("gansu:filter:xzxk",info["company"]):
						local_VQ_conn.lpush("gansu:company_id",json.dumps(info))
					else:
						print(info["company"]+" :重复数据!!")
				else:
					print(item)
					continue

		client = MongoClient(host='192.168.5.167', port=27017)
		collection=client["gansu"]["sorcomp"]
		# last_id =ObjectId("67489ff6779e716dade3fdd6")
		last_id =None
		currentPage =0
		pageSize = 1000
		total_copied =0
		futures=[]
		while True:
			query = {}
			if last_id:
				query["_id"] = {"$gt": last_id}  # 基于 _id 分页
			docs_cursor = collection.find(query).sort("_id", 1).limit(pageSize)
			docs = list(docs_cursor)
			if not docs:  # 如果没有数据，退出循环
				print("sorcomp 没有更多数据需要复制。")
				break
			futures.append(workers.submit(copy, docs))
			total_copied += len(docs)
			last_id = docs[-1]["_id"]
			currentPage += 1
			if len(futures) >= 20:
				for future in futures:
					future.result()
		for future in futures:
			future.result()
		print(f"数据库sorcomp 完成数据上传，成功上传 {total_copied} 条记录。")


if __name__ == '__main__':
	demo()


