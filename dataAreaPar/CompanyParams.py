import redis
import json
from datetime import datetime, timedelta
from loguru import logger


conn = redis.Redis(host='182.43.38.79',port=6379,db=5,password="lzh990130")


def getAreaID(area):
    nationwide = conn.smembers("cityAreaID")
    for item in nationwide:
        if json.loads(item.decode("utf-8"))["name"] == area:
            citys = json.loads(item.decode("utf-8"))['city']
            cityList = list()
            for city in citys:
                for item in city["district"]:
                    item.update({'base': city["base"]})
                    cityList.append(item)
            return cityList


def data_swit():
    # 初始日期
    start_date = datetime.strptime("2000-01-01", "%Y-%m-%d")
    # 结束日期
    end_date = datetime.strptime("2005-12-31", "%Y-%m-%d")
    current_date = start_date
    while current_date <= end_date:
        new_date = current_date.strftime("%Y-%m-%d")
        next_day = current_date + timedelta(days=1)
        next_date = next_day.strftime("%Y-%m-%d")
        current_date += timedelta(days=1)
        # 转成时间戳
        new_day = int(datetime.strptime(new_date, "%Y-%m-%d").timestamp() * 1000)
        next_day= int(datetime.strptime(next_date, "%Y-%m-%d").timestamp() * 1000)
        yield new_day,next_day,new_date,next_date


def run(area):
    _ = 0
    citylist=getAreaID(area)
    for info in citylist:
        for new_day,next_day,new_date,next_date in data_swit():
            info["new_day"] = new_day
            info["next_day"] = next_day
            info["new_date"] = new_date
            info["next_date"] = next_date
            conn.lpush("zhejiang:params:00_05", json.dumps(info))
            logger.info(f"第{_}:{info}保存完成！！")
            _ += 1

area=input()
run(area)