#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :demo.py
# @Time      :2024/10/27 12:59
# @Author    :18k


from lxml import etree

with open("1.html","r",encoding="utf-8") as f:
    pageinfo=f.read()

html=etree.HTML(pageinfo)
data=html.xpath("//script[@id='__NEXT_DATA__']/text()")[0]
print(data)














if __name__ == "__main__":
    run_code = 0
    pass
