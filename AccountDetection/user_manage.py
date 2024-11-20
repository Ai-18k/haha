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
import time
from feapder.network.user_agent import get
from simpleLogin import Login_module
from loguru import logger
from concurrent.futures import ThreadPoolExecutor
from retrying import retry
import redis

# conn = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123",socket_connect_timeout=70)
# local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=70)
local_VQ_conn = redis.Redis(host='192.168.5.181', port=7933, db=0, password="fer@nhaweif576KUG",socket_connect_timeout=70)


@retry(wait_fixed=1)
def proxy_list():
    proxyAddr = "tun-yowmaw.qg.net:17228"
    authKey = "17C8C7A6"
    password = "F825824D03DC"
    proxyUrl = "http://%(user)s:%(password)s@%(server)s" % {
        "user": authKey,
        "password": password,
        "server": proxyAddr,
    }
    proxies = {
        "http": proxyUrl,
        "https": proxyUrl,
    }
    # resp = requests.get("https://myip.ipip.net", proxies=proxies)
    # if resp.status_code == 200:
    # return proxies
    return None
    # else:
    #     raise Exception("请求代理")

class UserScreen():

        def __init__(self):
            self.V_num=0
            self.error_list=list()


        def is_VIP(self, mobil, num):
            try:
                ua = get()
                proxy = proxy_list()
                result = Login_module(mobil).main(proxy, ua)
                if result:
                    session, res = result
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
                    response = session.get(url, headers=headers, params=params)
                    response.encoding="utf-8"
                    logger.info(response.status_code)
                    logger.info(response.text)
                    if response.status_code == 200:
                        if "isVip" in response.json()["data"]:
                            logger.success(f"【*】会员用户:{mobil}!!")
                            with open("C:/Users/Administrator/Desktop/会员账号.txt", "a", encoding="utf-8") as f:
                                f.write(mobil["mobil"] + "密码" + mobil["pwd"] + "\n")
                                if local_VQ_conn.sadd("临时手机号过滤",mobil["mobil"]):
                                    # local_VQ_conn.lpush("memeryUser", json.dumps({"mobil": mobil["mobil"], "pwd": mobil["pwd"]}))
                                    local_VQ_conn.lpush("searchMobil", json.dumps({"mobil": mobil["mobil"], "pwd": mobil["pwd"]}))
                                    # local_VQ_conn.lpush("sifaUser", json.dumps({"mobil": mobil["mobil"], "pwd": mobil["pwd"]}))
                                    # local_VQ_conn.lpush("testMobil", json.dumps({"mobil": mobil["mobil"], "pwd": mobil["pwd"]}))
                                    logger.success(f"新增会员：{mobil}")
                                    self.V_num+=1
                        else:
                            logger.error(f"{mobil}未开通会员!!")
                            with open("C:/Users/Administrator/Desktop/未开会员账号.txt", "a", encoding="utf-8") as f:
                                f.write(mobil["mobil"] + "密码" + mobil["pwd"] + "\n")
                            local_VQ_conn.lpush("LoginUser", json.dumps({"mobil": mobil["mobil"], "pwd": mobil["pwd"]}))
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
                        if local_VQ_conn.sadd("临时去重mobilSet",user[0].strip()):
                            print(user[0])
                            with open("去重账号.txt", "a", encoding="utf-8") as f:
                                f.write(user[0].strip() + "密码" + user[1].strip() + "\n")
                        else:
                            print(f"重复账号:{user[0].strip()}")
                    else:
                        logger.success("已全部检测完成!")
                # time.sleep(3)
                local_VQ_conn.delete("临时去重mobilSet1")
            except IndexError as e:
                logger.error(e)


        def checkStute(self):
            ALLmoBIL=local_VQ_conn.lrange("ErrorMobil",0,-1)
            with ThreadPoolExecutor(4) as f:
                m_list=[]
                _=1
                for mobil in ALLmoBIL:
                    mobil=json.loads(mobil)
                    print(mobil)
                    if local_VQ_conn.sadd("临时手机号过滤",mobil["mobil"]):
                        res=f.submit(self.is_VIP, mobil=mobil, num=_)
                        m_list.append(res)
                    else:
                        logger.error(f"存在重复数据:{mobil}")
                    _+=1
                for future in m_list:
                    future.result()
                    logger.info(self.error_list)


        def run(self):
            res=local_VQ_conn.lrange("memeryUser",0,-1)
            res1=local_VQ_conn.lrange("searchMobil",0,-1)
            res2=local_VQ_conn.lrange("sifaUser",0,-1)
            res3=local_VQ_conn.lrange("LoginUser",0,-1)
            res5=local_VQ_conn.smembers("ErrorUser")
            res6=local_VQ_conn.smembers("ErrorPwd")
            for w in res:
                info=json.loads(w.decode("utf-8"))
                local_VQ_conn.sadd("临时手机号过滤",info["mobil"])
            for w2 in res1:
                info=json.loads(w2.decode("utf-8"))
                local_VQ_conn.sadd("临时手机号过滤",info["mobil"])
            for w3 in res2:
                info=json.loads(w3.decode("utf-8"))
                local_VQ_conn.sadd("临时手机号过滤",info["mobil"])
            for w4 in res3:
                info=json.loads(w4.decode("utf-8"))
                local_VQ_conn.sadd("临时手机号过滤",info["mobil"])
            for w6 in res5:
                info=json.loads(w6.decode("utf-8"))
                local_VQ_conn.sadd("临时手机号过滤",info["mobil"])
            for w7 in res6:
                info=json.loads(w7.decode("utf-8"))
                local_VQ_conn.sadd("临时手机号过滤",info["mobil"])
            # self.main()
            try:
                # result = open("去重账号.txt", encoding="utf-8").readlines()
                # result = open("待筛选的用户名密码.txt", encoding="utf-8").readlines()
                result = open("入库.txt", encoding="utf-8").readlines()
                # result =local_VQ_conn.lrange("test",0,-1)
                with ThreadPoolExecutor(4) as f:
                    _ = 0
                    m_list=[]
                    for line in result[::-1]:
                    # for line in result:
                        if line:
                            if isinstance(line, str):
                                user = line.strip().split("密码")
                                mobil = {"mobil": user[0].strip(), "pwd": user[1].strip()}
                                print("str >>>>>>>>>> ",mobil)
                            elif isinstance(line, bytes):
                                mobil=json.loads(line)
                                print("dict >>>>>>>>> ",mobil)
                            else:
                                logger.error("请输入正确的数据格式！！")
                                raise Exception("格式不正确!!")
                            if not local_VQ_conn.sismember("临时手机号过滤",mobil["mobil"]):
                                res=f.submit(self.is_VIP, mobil=mobil, num=_)
                                m_list.append(res)
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
