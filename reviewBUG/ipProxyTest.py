#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :ipProxyTest.py
# @Time      :2024/12/13 13:28
# @Author    : 18k
import random
import sys
import os

from retrying import retry

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)
# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)
import requests
from lxml import etree

@retry(wait_fixed=1000)
def proxy_list():
    # 隧道域名:端口号
    tunnel = "d152.kdltps.com:15818"
    # 用户名密码方式
    username = "t13206952228334"
    password = "wtx4i2in:%d" % random.randint(1, 8)
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
    }
    resp = requests.get("https://myip.ipip.net", proxies=proxies)
    if resp.status_code == 200:
        print(resp.text)
        return proxies
    else:
        raise Exception("代理异常！！")


def request():
    proxy=proxy_list()
    print(proxy)
    session = requests.session()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "$Cookie": "JSESSIONIDGS8=wmO4vqTylb-p6R-UKp-Fo-3IprarQclKweTnXphFwDlENHfQbjnu\\u0021-72404338; HMF_CI=f910e68f7d0864890212c9b6bf0ea38e0f46feb985f93f8c5bb3a6af2a802f35e1c9d72523013e024aef93e420f1fea6a80551b5b4183756053595a74b2e027d67; CSH_DF=9BdKpzliJ+KmrAT2Hs3i4zmzVd3sY6meJfwYiIaJsoSFhzTV/s55u0Psf2qRbzkL04; CSH_UF=f51bb482c660d0eeadd1f058058a2b35; HMY_JC=b3d97b9b77b1ca2d73338d3035413c3821c0fd6dcd8f91473bcb7fad567ead6ec3,; cookieinsert=20111186; HBB_HC=9b45dec85c64d6f2312d6f00939d6e446946d8eba4bfd365f072127e56a899ab356550aeb6b510a8ad6f41d9f77bdf22f5",
        "Origin": "http://htgs.ccgp.gov.cn",
        "Pragma": "no-cache",
        "Referer": "http://htgs.ccgp.gov.cn/GS8/contractpublish/index",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    url = "http://htgs.ccgp.gov.cn/GS8/contractpublish/search"
    params = {
        "contractSign": "0"
    }
    data = {
        "codeResult": "47aac16d685af2cca74c006b7e7eb674",
        "searchContractCode": "",
        "searchContractName": "",
        "searchProjCode": "",
        "searchProjName": "",
        "searchPurchaserName": "",
        "searchSupplyName": "",
        "searchAgentName": "",
        "searchPlacardStartDate": "2024-12-03",
        "searchPlacardEndDate": "2024-12-12",
        "code": "cshk"
    }
    session.post(url, headers=headers, params=params, data=data, proxies=proxy)
    session.headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Referer": "http://htgs.ccgp.gov.cn/GS8/contractpublish/search?contractSign=0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    }
    for page in range(1, 110):
        if page < 3:
            session.headers.update({"Referer": "http://htgs.ccgp.gov.cn/GS8/contractpublish/index_%d" % (page - 1)})
        url = "http://htgs.ccgp.gov.cn/GS8/contractpublish/index_%d" % page
        response = session.get(url,proxies=proxy)
        html = etree.HTML(response.text)
        uls = html.xpath('//ul[@class="ulst"]/li')
        for ul in uls:
            url = ul.xpath('./a/@href')
            title = ul.xpath('./a/@title')
            print(title, url)


if __name__ == "__main__":
    request()
    run_code = 0
    pass
