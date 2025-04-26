#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :winApi-wechat.py
# @Time      :2024/12/5 10:00
# @Author    : 18k
import re
import sys
import os

from pymongo import MongoClient

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)
# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)

serv_client = MongoClient(host='192.168.5.167', port=27017, retryWrites=True)
testdb=serv_client["shanghai"]["sorcomp"]

com=testdb.find_one({"name":"上海鋆鎏贸易有限公司航南公路店"})
print(com)

item_info={}

item_info["registered_capital"] = com["regCapital"] if com["regCapital"] else None

try:
    match = re.findall(r"实缴资本(.*?)人民币", com["abstractsBaseInfo"])
    if match:
        # 获取匹配到的内容
        item_info["contributed_capital"] = match[0]
    else:
        item_info["contributed_capital"] = None
except:
    item_info["contributed_capital"] = None

print(item_info)


if __name__ == "__main__":
    run_code = 0
    pass
