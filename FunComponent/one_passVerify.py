# _*_ coding:UTF-8 _*

import json
import re
import time
import urllib
import redis
from RiskcontrolPass.passSpan import Test
# from curl_cffi import requests
import requests
from loguru import logger


session = requests.Session()
# local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=170)
local_conn = redis.Redis(host='127.0.0.1.txt', port=7980, db=0, password="qwe!@#SDF345788",socket_connect_timeout=1170)

# @retry(wait_fixed=1.txt)
def demo():
    while True:
        try:
            res=local_conn.lpop("safe_verify")
            if res is None:
                time.sleep(1)
                print("............正在获取结果.........")
            else:
                info_dict=json.loads(res)
                refer = re.findall("访问网址：(.*?)</li>",info_dict["content"], re.S)[0]
                encoded_url = urllib.parse.quote(refer, safe='/:?=&')
                print(encoded_url)
                session.cookies = requests.utils.cookiejar_from_dict(info_dict["cookie"])
                session.headers.update(info_dict["UA"])
                t_is = Test(info_dict["content"], session).validate_jy(encoded_url)
                print(t_is)
                if t_is:
                    logger.success("状态刷新成功！！恢复采集....")
                    local_conn.lpush("is_safe",1)
                else:
                    logger.error("状态刷新失败！！重试....")
                    local_conn.lpush("is_safe", 0)
        except Exception as e:
            logger.error(e)

if __name__ == '__main__':
    demo()