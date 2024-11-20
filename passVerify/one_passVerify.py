# _*_ coding:UTF-8 _*

import json
import re
import time
from redis import Redis
from passSpan import Test
from requests import session
from requests import utils
from loguru import logger

session = session()
local_conn = Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=170)

def demo():
    while True:
        try:
            res=local_conn.lpop("safe_verify")
            if res is None:
                time.sleep(0.05)
                # print("............正在获取结果.........")
            else:
                info_dict=json.loads(res)
                refer = re.findall("访问网址：(.*?)</li>",info_dict["content"], re.S)[0]
                session.cookies = utils.cookiejar_from_dict(info_dict["cookie"])
                session.headers.update(info_dict["UA"])
                t_is = Test(info_dict["content"], session).validate_jy(refer)
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
