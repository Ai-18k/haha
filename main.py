import json
import threading
import time
import redis
import requests
from dataSpider.DataAreaSpider.v3_dataAreaV1 import SuccessCODE
from params.dataParams import run
from queue import Queue
from dataSpider.Detaildata.mainSpiderV1 import DetailSpider
import execjs
execjs.compile()

class runSpider():
    def __init__(self):
            self.conn = redis.Redis(host='182.43.38.79', port=6379, db=5, password="lzh990130", socket_connect_timeout=70)
            self.l_params=Queue()
            self.l_com_id=Queue()
            self.l_detail_data=Queue()
            self.l_sifa=Queue()
            self.l_zlxx=Queue()

    def get_params(self):
        for info in run():
            print(info)
            self.l_params.put(info)
            # break

    def get_com_id(self,Request):
        while True:
            info=self.l_params.get()
            print(info)
            allIDs=SuccessCODE(Request).main_id(info)
            if allIDs:
                for company_id in allIDs:
                    print(company_id)
                    self.l_com_id.put(company_id)
                    self.l_params.task_done()
                # break

    def get_detail(self):
        while True:
            company_id=self.l_com_id.get()
            results=DetailSpider().main(company_id)
            for detail_data in results:
                print(detail_data)
                self.l_detail_data.put(detail_data)
            self.l_com_id.task_done()
            # break


    def main(self):
        while True:
            res = self.conn.lpop("detailCookie")
            if res is None:
                time.sleep(0.5)
            else:
                self.Reqest = json.loads(res.decode("utf-8"))
                print(self.Reqest)

                t_list = []
                # 1.txt. 获取参数线程
                t_url = threading.Thread(target=self.get_params)
                t_list.append(t_url)

                # 2. 获取id线程启动
                for i in range(2):
                    t_data = threading.Thread(target=self.get_com_id,kwargs={"Request":self.Reqest})
                    t_list.append(t_data)

                # # 3. 解析详情数据
                # for i in range(2):
                #     t_parse = threading.Thread(target=self.get_detail)
                #     t_list.append(t_parse)

                # #4.司数据
                # for i in range(2):
                #     t_parse = threading.Thread(target=self.sfaj)
                #     t_list.append(t_parse)
                #
                # # 5.专利数据
                # for i in range(2):
                #     t_parse = threading.Thread(target=self.zlxx)
                #     t_list.append(t_parse)
                #
                # # 6.其他司法数据
                # for i in range(2):
                #     t_parse = threading.Thread(target=self.zlxx)
                #     t_list.append(t_parse)
                #
                # # 6.其他历史司法数据
                # for i in range(2):
                #     t_parse = threading.Thread(target=self.zlxx)
                #     t_list.append(t_parse)


                # # 4.保存数据线程
                # t_save = threading.Thread(target=self.save_data)
                # t_list.append(t_save)

                # # 4.数据发送服务器线程
                # t_save = threading.Thread(target=self.save_data)
                # t_list.append(t_save)

                for t in t_list:
                    t.setDaemon(True) # 把子线程设置为守护主线程,  主线程结束, 子线程就结束
                    t.start()

                time.sleep(10)
                for q in [self.l_params,self.l_com_id
                    # ,self.l_detail_data
                    # ,self.l_sifa,self.l_zlxx
                          ]:
                    q.join()

if __name__ == '__main__':
    rs=runSpider()
    rs.main()
    # rs.get_params()
    # rs.get_com_id()













