#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :demo.py
# @Time      :2025/1/14 19:41
# @Author    : 18k
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)
# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)


import execjs

with open("4.js", encoding="utf-8") as f:
    jscode = f.read()
IfMatch = execjs.compile(jscode).call("verify", "6fdea3c55fe64f43be2d70976fe6b15c","83df451bed80ab4580bc7203014858ea")
print(IfMatch)


if __name__ == "__main__":
    run_code = 0
    pass
