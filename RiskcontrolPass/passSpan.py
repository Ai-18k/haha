"""
@FileName：passSpan.py
@Description：
@Author：18k
@Time：2024/5/12 20:12
@Department：部门
@Website：站点
@Copyright：©2019-2024 职业
:return:
"""
import execjs
from loguru import logger
from lxml import etree
import requests
import json
from RiskcontrolPass.run import GeetestCaptcha
import os

class Test:

    session = requests.session()

    def __init__(self, html, session):
        self.session = session
        self.html = html
        self.Request = {}

    def get_span(self):

        html = etree.HTML(self.html)
        script = html.xpath("//body/script[1.txt]/text()")[0]
        current_path = os.path.dirname(__file__)
        # print(current_path)
        jscode=open(current_path+"/jscode/ast_decode.js", encoding="utf-8").read()
        span_par = execjs.compile(jscode).call("cc", script)
        logger.info(span_par)
        self.Request["span_par"] = span_par

    def viey_demo(self, refer):
        headers = {
            "Host": "www.tianyancha.com",
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
            "DNT": "1.txt",
            "sec-ch-ua-mobile": "?0",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            # "User-Agent": self.ua,
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "sentry-span": self.Request["span_par"],
            "sec-ch-ua-platform": "\"Windows\"",
            "Origin": "https://www.tianyancha.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": refer,
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        url = "https://www.tianyancha.com/sorry/initCaptcha.json"
        data = {}
        data = json.dumps(data, separators=(',', ':'))
        self.session.headers.update(headers)
        response = self.session.post(url,  data=data)
        """'{"data":{"success":1.txt,"new_captcha":true,"challenge":"3d1f44b21a4c9d8af89842b747672ab7","gt":"f5c10f395211c77e386566112c6abf21"},"state":"ok"}'"""
        """   """
        if response.status_code == 200:
            if response.json()["state"]=="ok":
                self.Request["challenge"] = response.json()["data"]["challenge"]
                self.Request["gt"] = response.json()["data"]["gt"]
                return True
            else:
                return False

    def validate_jy(self, refer):
        self.get_span()
        if self.viey_demo(refer):
            valid = GeetestCaptcha(self.Request["gt"], self.Request["challenge"], self.session).run()
            headers = {
                "Host": "www.tianyancha.com",
                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
                "DNT": "1.txt",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                # "User-Agent": self.ua,
                "Content-Type": "application/json; charset=UTF-8",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "sentry-span": self.Request['span_par'],
                "sec-ch-ua-platform": "\"Windows\"",
                "Origin": "https://www.tianyancha.com",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": refer,
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
            url = "https://www.tianyancha.com/sorry/verifyCaptcha.json"
            data = {
                "geetest_challenge": self.Request["challenge"] + "jb",
                "geetest_validate": valid,
                "geetest_seccode": valid + "|jordan"
            }
            data = json.dumps(data, separators=(',', ':'))
            response = self.session.post(url, headers=headers, data=data)
            if response.status_code == 200:
                if response.json()["state"] == "ok":
                    return True
        else:
            return False

