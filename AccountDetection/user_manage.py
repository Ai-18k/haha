#!/usr/bin/env python
# encoding: utf-8

"""
@FileName：user_manage.py
@Description：管理的登录信息
@Author：18k
@Time：2024/5/21 18:40
@Department：部门
@Website：站点
@Copyright：©2019-2024 职业
:return:
"""
import json
import random
import time
import requests
from feapder.network.user_agent import get
from retrying import retry
from config import checkconfig
from simpleLogin import Login_module
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
import redis


class UserScreen():

        def __init__(self):
            self.config = checkconfig("bendi")
            self.local_VQ_conn = redis.Redis("192.168.5." + self.config["uAddr"][0],
                                             self.config["uAddr"][1],
                                             self.config["uAddr"][2],
                                             self.config["uAddr"][3],
                                             socket_connect_timeout=1155)
            self.local_conn = redis.Redis("192.168.5." + self.config["fAddr"][0],
                                          self.config["fAddr"][1],
                                          self.config["fAddr"][2],
                                          self.config["fAddr"][3],
                                          socket_connect_timeout=1170)
            self.session=requests.session()
            self.V_num=0
            self.error_list=list()

        @retry(wait_fixed=1000)
        def proxy_list(self):
            if self.config["proxy"]:
                global l
                l = random.randint(1, 6)
                # 隧道域名:端口号
                tunnel = self.config["proxy"][2]
                # 用户名密码方式
                username = self.config["proxy"][0]
                password = "%s:%d" % (self.config["proxy"][1], l)
                proxies = {
                    "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
                    "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
                }
                # try:
                #     resp = requests.get("https://myip.ipip.net", proxies=proxies, timeout=(4, 15))
                #     if resp.status_code == 200:
                #         print(resp.text)
                #         return proxies
                #     else:
                return None
                # except requests.Timeout as e:
                #     logger.error(e)
                #     return None
                # except requests.ConnectionError as e:
                #     logger.error(e)
                #     raise "代理异常"
            else:
                return None

        def is_VIP(self, mobil, num):
            try:
                ua = get()
                proxy = self.proxy_list()
                result = Login_module(mobil).main(proxy, ua)
                if result:
                    self.session, res = result
                    with open("C:/Users/Administrator/Desktop/可以登录账号.txt", "a", encoding="utf-8") as f:
                        f.write(mobil["mobil"] + "密码" + mobil["pwd"] + "\n")
                    headers = {
                        "Accept": "application/json, text/plain, */*",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Content-Type": "application/json",
                        "Origin": "https://www.tianyancha.com",
                        "Pragma": "no-cache",
                        "Referer": "https://www.tianyancha.com/",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-site",
                        "User-Agent": ua,
                        "X-AUTH-TOKEN": res["auth_token"],
                        "X-TYCID": res["sign"],
                        "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": "\"Windows\""
                    }
                    url = "https://napi-huawei.tianyancha.com/next/web/getUserInfo"
                    params = {
                        "_": str(int(time.time() * 1000))
                    }
                    response =self.session.get(url, headers=headers, params=params,proxies=proxy)
                    response.encoding="utf-8"
                    logger.info(response.status_code)
                    print(response.text)
                    if response.status_code == 200:
                        if "isVip" in response.json()["data"]:
                            logger.success(f"【*】会员用户:{mobil}!!")
                            with open("C:/Users/Administrator/Desktop/会员账号.txt", "a", encoding="utf-8") as f:
                                f.write(mobil["mobil"] + "密码" + mobil["pwd"] + "\n")
                                if self.local_VQ_conn.sadd("临时手机号过滤",mobil["mobil"]):
                                    # self.local_VQ_conn.lpush("memeryUser", json.dumps({"mobil": mobil["mobil"], "pwd": mobil["pwd"]}))
                                    self.local_VQ_conn.lpush("searchMobil", json.dumps({"mobil": mobil["mobil"], "pwd": mobil["pwd"]}))
                                    # self.local_VQ_conn.lpush("sifaUser", json.dumps({"mobil": mobil["mobil"], "pwd": mobil["pwd"]}))
                                    # self.local_VQ_conn.lpush("testMobil", json.dumps({"mobil": mobil["mobil"], "pwd": mobil["pwd"]}))
                                    logger.success(f"新增会员：{mobil}")
                                    self.V_num+=1
                        else:
                            logger.error(f"{mobil}未开通会员!!")
                            with open("C:/Users/Administrator/Desktop/未开会员账号.txt", "a", encoding="utf-8") as f:
                                f.write(mobil["mobil"] + "密码" + mobil["pwd"] + "\n")
                            self.local_VQ_conn.lpush("LoginUser", json.dumps({"mobil": mobil["mobil"], "pwd": mobil["pwd"]}))
                    else:
                        logger.error(f"{mobil}:账号异常!!")
                    logger.info(f"这是第{num}个账号:{mobil}检测完毕！！")
                else:
                    self.error_list.append(mobil)
                logger.info(f"一共 {self.V_num} 新增会员!!!")
            except Exception as e:
                logger.error(e)


        def main(self):
            try:
                result = open("待筛选的用户名密码.txt", encoding="utf-8").readlines()
                # result = open("入库.txt", encoding="utf-8").readlines()
                for line in result:
                    if line:
                        user = line.strip().split("密码")
                        if self.local_VQ_conn.sadd("临时去重mobilSet",user[0].strip()):
                            print(user[0])
                            with open("去重账号.txt", "a", encoding="utf-8") as f:
                                f.write(user[0].strip() + "密码" + user[1].strip() + "\n")
                        else:
                            print(f"重复账号:{user[0].strip()}")
                    else:
                        logger.success("已全部检测完成!")
                # time.sleep(3)
                self.local_VQ_conn.delete("临时去重mobilSet")
            except IndexError as e:
                logger.error(e)


        def checkStute(self):
            ALLmoBIL=self.local_VQ_conn.lrange("ErrorMobil",0,-1)
            with ThreadPoolExecutor(4) as f:
                m_list=[]
                _=1
                for mobil in ALLmoBIL:
                    mobil=json.loads(mobil)
                    print(mobil)
                    if self.local_VQ_conn.sadd("临时手机号过滤",mobil["mobil"]):
                        res=f.submit(self.is_VIP, mobil=mobil, num=_)
                        m_list.append(res)
                    else:
                        logger.error(f"存在重复数据:{mobil}")
                    _+=1
                for future in m_list:
                    future.result()
                    logger.info(self.error_list)

        def run(self):
            res=self.local_VQ_conn.lrange("memeryUser",0,-1)
            res1=self.local_VQ_conn.lrange("searchMobil",0,-1)
            res2=self.local_VQ_conn.lrange("sifaUser",0,-1)
            res3=self.local_VQ_conn.lrange("LoginUser",0,-1)
            res5=self.local_VQ_conn.smembers("ErrorUser")
            res6=self.local_VQ_conn.smembers("ErrorPwd")
            for w in res:
                info=json.loads(w.decode("utf-8"))
                self.local_VQ_conn.sadd("临时手机号过滤",info["mobil"])
            for w2 in res1:
                info=json.loads(w2.decode("utf-8"))
                self.local_VQ_conn.sadd("临时手机号过滤",info["mobil"])
            for w3 in res2:
                info=json.loads(w3.decode("utf-8"))
                self.local_VQ_conn.sadd("临时手机号过_滤",info["mobil"])
            for w4 in res3:
                info=json.loads(w4.decode("utf-8"))
                self.local_VQ_conn.sadd("临时手机号过滤",info["mobil"])
            for w6 in res5:
                info=json.loads(w6.decode("utf-8"))
                self.local_VQ_conn.sadd("临时手机号过滤",info["mobil"])
            for w7 in res6:
                info=json.loads(w7.decode("utf-8"))
                self.local_VQ_conn.sadd("临时手机号过滤",info["mobil"])
            # self.main()
            try:
                # result = open("去重账号.txt", encoding="utf-8").readlines()
                result = open("入库.txt", encoding="utf-8").readlines()
                with ThreadPoolExecutor(3) as f:
                    _ = 0
                    m_list=[]
                    for line in result:
                        if line:
                            if isinstance(line, str):
                                user = line.strip().split("密码")
                                mobil = {"mobil": user[0].strip(), "pwd": user[1].strip()}
                                print("str >>>>>>",mobil)
                            elif isinstance(line, bytes):
                                mobil=json.loads(line)
                                print("dict >>>>>>",mobil)
                            if not self.local_VQ_conn.sismember("临时手机号过滤",mobil["mobil"]):
                                res=f.submit(self.is_VIP, mobil=mobil, num=_)
                                m_list.append(res)
                                # self.is_VIP(mobil,_)
                            else:
                                logger.error(f"存在重复数据:{mobil}")
                        else:
                            logger.success("已全部检测完成!")
                            break
                        _ += 1
                        logger.success(f"共检测 【{_}】 个账号！！")
                    for future in m_list:
                        future.result()
                # logger.info(self.error_list)
            except Exception as e:
                logger.error(e)


if __name__ == '__main__':
    UserScreen().run()
    # UserScreen().main()
    # UserScreen().checkStute()
