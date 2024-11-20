# _*_ coding:UTF-8 _*
import json
import random
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from loguru import logger
from redis.client import Redis
# from Login.asyncio_demo import login
from FunComponent.AccountDetection.user_manage import UserScreen


moduel_path="tmp/mobil.txt"

class SMobil(UserScreen):
    def __init__(self):
        super().__init__()
        self.mobil_pool=Queue()
        self.local_E5_conn =Redis(host='192.168.5.76', port=8490, db=0, password="#Tn=EP(q%{", socket_connect_timeout=70)

    def redfile(self,filepath):
        mobils=open(filepath,encoding="utf-8").readlines()
        for mobil in mobils:
            yield mobil

    def analyze(self,mobil):
        if isinstance(mobil,str):
            if mobil:
                user = mobil.strip().split("密码")
                # print(user)
                mobil = {"mobil": user[0], "pwd": user[1]}
                return mobil
        elif isinstance(mobil,dict):
            return mobil
        else:
            print(mobil)
            raise TypeError("格式错误！")

    def CSameMobil(self,data):
        # 统计每个 "pwd" 出现的次数
        values = [item["pwd"] for item in data]
        value_count = Counter(values)
        # 对 "pwd" 出现次数进行排序
        sorted_values = sorted(value_count.items(), key=lambda x: x[1], reverse=True)
        # print(sorted_values)
        """ 处理手机号  根据密码频率排名  提取手机号前三位生成手机号，并且关联该密码 """
        # 根据重复的 "pwd" 找到对应的 "mobil"，统计 "mobil" 的前三位重复度并排序
        key_count = {}
        for value, count in sorted_values:
            # 找到对应的 "mobil"
            keys = [item["mobil"] for item in data if item["pwd"] == value]
            # 统计 "mobil" 的前三位重复度
            key_prefix_count = Counter([key[:3] for key in keys])
            # 对 key_prefix_count 进行排序，并保存在 key_count 中
            sorted_key_prefix = sorted(key_prefix_count.items(), key=lambda x: x[1], reverse=True)
            key_count[value] = sorted_key_prefix
        # 输出结果
        print("按 pwd 排序的重复值及对应 mobil前三位的重复度：")
        for value, prefixes in key_count.items():
            print(f"Value: {value}")
            print("前三位重复的 mobil：")
            for prefix, count in prefixes:
                print(f"mobil前缀: {prefix}, 出现次数: {count}")
                print(f"{prefix}: {value}")
                yield {f"{prefix}":f"{value}"}

    def generateMobil(self,mobil):
        # print(mobil)
        # # phones = [f"list(mobil.keys())[0]{i:08d}" for i in range(100000000)]
        # for i in range(100000000):
        #     phones = list(mobil.keys())[0]+f"{i:08d}"
        #     # print({f"{phones}": f"{mobil[list(mobil.keys())[0]]}"})
        #     user=dict()
        #     user["mobil"]=phones
        #     user["pwd"] = mobil[list(mobil.keys())[0]]
        #     yield  user
        while True:
            g_list = ["131", "155"]
            for g in g_list:
                nlist = "".join(random.choices(["0", "1.txt", "2", "3", "4", "5", "6", "7", "8", "9"], k=8))
                m_dic = dict()
                m_dic["mobil"] = g + nlist
                m_dic["pwd"] = "hh123456"
                print(m_dic)
                yield m_dic
            # self.mobil_pool.put(user)
            # break


    def main(self):
        with ThreadPoolExecutor(5) as f:
            data=[self.analyze(mobil) for mobil in self.redfile(moduel_path)]
            futures = []
            for mobil in self.CSameMobil(data):
                for user in self.generateMobil(mobil):
                    print(user)
                    if self.local_E5_conn.sadd("生成手机号过滤",json.dumps(user)):
                        futures.append(f.submit(UserScreen().is_VIP,mobil=user,num=1))
                    else:
                        logger.warning(f"重复user:{user}")
                    if len(futures)>=100:
                        for future in futures:
                            try:
                                future.result()
                            except Exception as e:
                                logger.error(e)
                                future.result()
                        futures.clear()
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logger.error(e)
                    future.result()

                # break


if __name__ == '__main__':
    SMobil().main()
    # CSameMobil()





