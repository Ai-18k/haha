#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :__init__.py.py
# @Time      :2024/12/13 11:25
# @Author    : 18k
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)
# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)

if __name__ == "__main__":
    run_code = 0
    pass
