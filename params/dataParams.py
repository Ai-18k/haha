"""
@FileName：param.py
@Description：
@Author：18k
@Time：2024/6/8 15:02
@Department：部门
@Website：站点
@Copyright：©2019-2024 职业
:return:
"""
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import redis
from loguru import logger


conn = redis.Redis(host='182.43.38.79', port=6379, db=5, password="lzh990130",socket_connect_timeout=70)
conn1 = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123",socket_connect_timeout=70)
# local_conn = redis.Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=70)
local_conn = redis.Redis(host='127.0.0.1', port=7980, db=0, password="qwe!@#SDF345788",socket_connect_timeout=70)


def getAreaID():
    nationwide = conn1.lrange("cityAreaID",0,-1)
    for item in nationwide:
        if json.loads(item.decode("utf-8"))["name"] == "河北省":
        # if json.loads(item.decode("utf-8"))["name"] == "广东省":
        # if json.loads(item.decode("utf-8"))["name"] == "山东省":
        # if json.loads(item.decode("utf-8"))["name"] == "上海市":
        # if json.loads(item.decode("utf-8"))["name"] == "浙江省":
            citys = json.loads(item.decode("utf-8"))['city']
            print(citys)
            cityList=list()
            for city in citys:
                for item in city["district"]:
                    item.update({'base': city["base"]})
                    # print(item)
                    cityList.append(item)
            return cityList

def data_swit():
    # 初始日期
    # start_date = datetime.strptime("2023-09-01",
    #                                "%Y-%m-%d")
    # # 结束日期
    # end_date = datetime.strptime("2023-12-30",
    #                              "%Y-%m-%d")  
    # 初始日期
    start_date = datetime.strptime("2000-01-01",
                                   "%Y-%m-%d")
    # 结束日期
    end_date = datetime.strptime("2024-09-10",
                                 "%Y-%m-%d")
    current_date = start_date
    while current_date <= end_date:
        new_date = current_date.strftime("%Y-%m-%d")
        next_day = current_date + timedelta(days=1)
        next_date = next_day.strftime("%Y-%m-%d")
        current_date += timedelta(days=1)
        new_day = int(datetime.strptime(new_date, "%Y-%m-%d").timestamp() * 1000)
        next_day = int(datetime.strptime(next_date, "%Y-%m-%d").timestamp() * 1000)
        print(new_day,next_day,new_date,next_date)
        # break
        yield new_day,next_day,new_date,next_date


def save_params(info):
    try:
        local_conn.lpush("test:params", json.dumps(info))
    except:
        local_conn.lpush("test:params", json.dumps(info))
    # try:
    #     conn1.lpush("test:params", json.dumps(info))
    # except:
    #     conn1.lpush("test:params", json.dumps(info))


def run():
    # orgType = ["有限责任公司", "股份有限公司", "集体所有制", "股份合作制", "国有企业",
    #            "个人独资企业", "有限合伙", "普通合伙", "外商投资企业", "港、澳、台", "联营企业", "私营企业"]
    _ = 0
    with ThreadPoolExecutor(3) as f:
        futures=[]
        for info in getAreaID():
            for new_day,next_day,new_date,next_date in data_swit():
                info["new_day"] = new_day
                info["next_day"] = next_day
                info["new_date"] = new_date
                info["next_date"] = next_date
                # for name in orgType:
                #     info["orgType"] = name
                print(info)
                futures.append(f.submit(save_params, info=info))
                # local_conn.sadd("test:params", json.dumps(info))
                # local_conn.lpush("test:2:params", json.dumps(info))
                logger.info(f"一共有{_}条数据！！")
                _ += 1
                if len(futures)>=30:
                    for future in futures:
                        future.result()
                    futures.clear()
        for future in futures:
            future.result()



if __name__ == '__main__':
    run()
