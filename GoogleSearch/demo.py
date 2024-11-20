import json
import random
import time
from concurrent.futures import ThreadPoolExecutor

import pika
import redis
from retrying import retry
from loguru import logger


# 配置文件路径
PROGRESS_FILE = 'progress.json'


class AA:
    def __init__(self):
        self.conn = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123", socket_connect_timeout=70)
        self.local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=70)
        self.local_T4_conn = redis.Redis(host='192.168.5.87', port=7933, db=0, password="fer@nhaweif576KUG",
                              socket_connect_timeout=170)
        self.page = 1

    def save_progress(self,page):
        """保存当前页面进度到文件"""
        with open(PROGRESS_FILE, 'w') as f:
            json.dump({'page': page}, f)

    def load_progress(self):
        """加载保存的页面进度"""
        try:
            with open(PROGRESS_FILE, 'r') as f:
                data = json.load(f)
                return data.get('page', 1)
        except FileNotFoundError:
            return 1

    @retry(wait_fixed=500,stop_max_attempt_number=5)
    def demo1(self):
        try:
            page=self.load_progress()
            while True:
                print(page)
                ee=int(random.random()*page)
                if ee<1:
                    print(page)
                    self.save_progress(page)
                    raise Exception("不正确")
                if ee>4:
                    raise Exception("SHIXIAO")
                logger.info("这是第%d页" % page)
        except Exception as e:
            logger.error(e)

    def demo2(self):
        pass

    def demo3(self):
        pass

    def demo4(self):
        # pass
        # for i in range(3):
        #     res=self.local_T4_conn.lpop("ErrorMobil")
        #     self.local_T4_conn.lpush("testUser",res)
        for i in range(1):
            res=self.local_conn.lpop("memeryUser")
            # self.local_T4_conn.lpush("test1User",res)
            # self.local_T4_conn.lpush("test1Mobil",res)
            self.local_T4_conn.lpush("testUser",res)
            # self.local_T4_conn.lpush("testMobil",res)


    def main(self):
        # with ThreadPoolExecutor(2) as f:
        #     futures = []
                # res=f.submit(self.demo1,page=i)
                # futures.append(res)
                self.demo4()

            # for future in futures:
            #     future.result()

        # pass

if __name__ == '__main__':
    AA().main()









