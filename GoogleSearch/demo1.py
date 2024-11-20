#!/usr/bin/python
# -*- coding: utf8 -*-

import requests


from bs4 import BeautifulSoup



def remove_html_and_css(text):

    soup = BeautifulSoup(text, 'lxml')
    for tag in soup.descendants:
        if hasattr(tag, 'attrs') and 'style' in tag.attrs:
            del tag['style']

    pure_text = ' '.join(soup.stripped_strings)

    return pure_text


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "DNT": "1.txt",
    "Pragma": "no-cache",
    "Referer": "https://www.google.co.jp/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1.txt",
    "Upgrade-Insecure-Requests": "1.txt",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
cookies = {
    "ASP.NET_SessionId": "ofkzujw01ivykzm4r4s4isz4",
    "__jsluid_s": "c0345ddbd47ca2800202bb8295b7d460",
    "Hm_lvt_62c73c53c0ae8c986919225c11b0ff19": "1726218931",
    "Hm_lpvt_62c73c53c0ae8c986919225c11b0ff19": "1726218931",
    "HMACCOUNT": "6BA7A9FB93E7C7C1",
    "kfauto": "1.txt"
}
url = "https://www.b2b168.com/c168-18677667.html"
response = requests.get(url, headers=headers, cookies=cookies)
response.encodeing="gbk"
res=response.text.replace("\xa9","")
tx=remove_html_and_css(res)
print(tx)
