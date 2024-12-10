#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :demo1.py
# @Time      :2024/11/10 3:53
# @Author    : 18k
import base64
import hashlib
import json
import re
import sys
import os
import time
import uuid
from datetime import datetime
import ddddocr
import execjs
import redis
import requests
from feapder.network.user_agent import get
from loguru import logger
from geetest4_word import get_word_position

session = requests.Session()
conn = redis.Redis(host='127.0.0.1', port=7980, db=0, password="qwe!@#SDF345788",socket_connect_timeout=70)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)
# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)


class CC1:
    def PostPic(self,pic_list):
        if len(pic_list) == 4:
            pic_list.append("")
        tmp = str(time.time())
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        }
        # url = "http://192.168.5.167:10121/geetest4_word/gradio_api/queue/"
        url = "http://127.0.0.1:1012/geetest4_word/gradio_api/queue/"
        params = {"": ""}
        data = {"data": pic_list,"fn_index": 1,"session_hash": tmp}
        data = json.dumps(data, separators=(',', ':'))
        requests.post(url + "join", headers=headers, params=params, data=data, verify=False)
        params = {"session_hash": tmp}
        response = requests.get(url + "data", headers=headers, params=params, verify=False)
        message_count = 0  # 初始化计数器
        # 逐行读取事件流数据
        for line in response.iter_lines(decode_unicode=True):
            if line:  # 跳过空行
                if line.startswith("data:"):
                    data = line[5:].strip()  # 去掉 "data:" 前缀并清理空格
                    message_count += 1
                    # 检查是否已接收到第三条消息
                    if message_count == 3:
                        xy = []
                        plan = json.loads(data)["output"]["data"][1]
                        for crop in plan:
                            x1, y1, x2, y2 = crop
                            xy.append([(x1 + x2) / 2, (y1 + y2) / 2])
                        return xy


ocr = ddddocr.DdddOcr(det=False, ocr=False)

def get_jy_gcaptcha4Code():

        ua=get()

        def get_1():
                uuid1 = uuid.uuid1()
                headers = {
                        "Host": "gcaptcha4.geetest.com",
                        "Pragma": "no-cache",
                        "Cache-Control": "no-cache",
                        "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
                        "DNT": "1",
                        "sec-ch-ua-mobile": "?0",
                        "User-Agent":ua,
                        "sec-ch-ua-platform": "\"Windows\"",
                        "Accept": "*/*",
                        "Sec-Fetch-Site": "cross-site",
                        "Sec-Fetch-Mode": "no-cors",
                        "Sec-Fetch-Dest": "script",
                        "Referer": "https://www.tianyancha.com/",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                }
                url = "https://gcaptcha4.geetest.com/load"
                params = {
                        # "callback": "geetest_1726673346207",
                        "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
                        "challenge": uuid1,
                        "client_type": "web",
                        "lang": "zho"
                }
                response =session.get(url, headers=headers, params=params)
                if response.status_code == 200:
                        cookies = response.cookies.get("captcha_v4_user")
                        resp = json.loads(response.text.strip("(").strip(")"))
                        type = resp["data"]['captcha_type']
                        lot_number =resp["data"]["lot_number"]
                        process_token =resp["data"]["process_token"]
                        pow_detail =resp["data"]["pow_detail"]
                        pow_detail = [pow_detail[i] for i in pow_detail if isinstance(pow_detail, dict)]
                        payload =resp["data"]["payload"]
                        static_path =resp["data"]["static_path"]
                        params_list = {
                                "captcha_id": "517df78b31ff1b8f841cd86fc0db9f3e",
                                "lot_number": lot_number,
                                "process_token": process_token,
                                "pow_detail": pow_detail,
                                "payload": payload,
                                "cookies": cookies,
                                "static_path": static_path
                        }
                        if type == 'word':
                                print(">>>>>>>>>>>>>>>>>>>>>>>>点选>>>>>>>>>>>>>>")
                                q_list = resp["data"]['ques']
                                # bytes_list = []
                                base_list = []
                                for index, img_url in enumerate(q_list):
                                        tag = requests.get("https://static.geetest.com/" + img_url).content
                                        # self.download_img(tag, str(index), type, uuid1)
                                        # word_pic = ImageProcess.wordprocess(tag)
                                        # word_pic = base64.b64encode(tag).decode("utf-8")
                                        # base_list.append(word_pic)
                                        base_list.append(tag)
                                imgs_url = "https://static.geetest.com/" + resp["data"]['imgs']
                                slide_bytes = requests.get(imgs_url).content
                                # new_pic = ImageProcess.mergePic(slide_bytes, bytes_list)
                                # new_pic = [base64.b64encode(slide_bytes).decode("utf-8")] + base_list
                                # click_list = CC().PostPic(new_pic)
                                click_list = get_word_position(slide_bytes, base_list)
                                click_smark = []
                                for _word in click_list:
                                        click_smark.append([round(int(_word[0]) * 100 / 3), round(int(_word[1]) * 50)])
                                logger.info(click_smark)
                                # self.download_img(slide_bytes, "click_img", type, uuid1)
                                params_list["smark"] = click_smark
                                params_list["type"] = "word"
                        elif type == 'slide':
                                print(">>>>>>>>>>>>>>>>>>>>>>>>滑块>>>>>>>>>>>>>>")
                                slide_url = "https://static.geetest.com/" + resp["data"]['slice']
                                bg_url = "https://static.geetest.com/" + resp["data"]['bg']
                                target_bytes = requests.get(slide_url).content
                                bg_bytes = requests.get(bg_url).content
                                dis = ocr.slide_match(target_bytes, bg_bytes, simple_target=True)["target"][0]
                                logger.info(dis)
                                params_list["dis"] = dis
                                params_list["type"] = "slide"
                        return params_list

        def re_jscodeV1(params_list):
            headers = {
                "Host": "static.geetest.com",
                "pragma": "no-cache",
                "cache-control": "no-cache",
                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                             "Chrome\";v=\"114\"",
                "origin": "https://www.tianyancha.com",
                "dnt": "1",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": ua,
                "sec-ch-ua-platform": "\"Windows\"",
                "accept": "*/*",
                "sec-fetch-site": "cross-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "script",
                "referer": "https://www.tianyancha.com/",
                "accept-language": "zh-CN,zh;q=0.9"
            }
            url = "https://static.geetest.com" + params_list["static_path"] + "/js/gcaptcha4.js"
            response = session.get(url, headers=headers)
            str_code = ""
            match = re.search(r'(.*?)\.', response.text, re.S)
            head = match.group().strip(".")
            matche_01 = re.findall(rf"{head}\..*?\}}\(\);", response.text, re.S)
            str_code += matche_01[0] + matche_01[1]
            matche_02 = re.findall(rf'{head}\..*?}};', response.text, re.S)
            str_code += matche_02[2] + matche_02[3] + f"function {head}() {{}};"
            matche_03 = re.findall(r"!function\(\)\s*\{[\s\S]*?\}\(\),", response.text, re.S)[0]
            pattern = r"!function\(\)\s*\{\s*!(.*?)\}\(\),"  # 匹配 function() 的块
            matche_04 = re.findall(pattern,matche_03, re.S)[0]  # 启用多行模式
            str_code+="var code=" + matche_04 + ";return [this._lib,this.lib._abo]}"
            res=execjs.compile(str_code).call("code")
            print(res)
            return {"head": head, "par_param": res[0], "keys": res[1],"content":response.text,"paramsList":params_list}

        def re_js_code(params_list):
            headers = {
                "Host": "static.geetest.com",
                "pragma": "no-cache",
                "cache-control": "no-cache",
                "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                             "Chrome\";v=\"114\"",
                "origin": "https://www.tianyancha.com",
                "dnt": "1",
                "sec-ch-ua-mobile": "?0",
                "User-Agent":ua,
                "sec-ch-ua-platform": "\"Windows\"",
                "accept": "*/*",
                "sec-fetch-site": "cross-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "script",
                "referer": "https://www.tianyancha.com/",
                "accept-language": "zh-CN,zh;q=0.9"
            }
            url = "https://static.geetest.com" + params_list["static_path"] + "/js/gcaptcha4.js"
            response =session.get(url, headers=headers)
            str_code = ""
            match = re.search(r'(.*?)\.', response.text, re.S)
            head = match.group().strip(".")
            matche_01 = re.findall(rf"{head}\..*?\}}\(\);", response.text, re.S)
            str_code += matche_01[0] + matche_01[1]
            matche_02 = re.findall(rf'{head}\..*?}};', response.text, re.S)
            str_code += matche_02[2] + matche_02[3] + f"function {head}() {{}};"
            pattern = r'!function\s*\(\)\s*{[^}]*}()'
            matche_03 = re.search(pattern, response.text, re.S)
            text = matche_03.group()
            matche_04 = re.search(r"var.*?.shift\(\);", text, re.S)
            str_code += "function get_param(){" + matche_04.group()
            # pattern = r'\{\s*"(\\u[0-9a-fA-F]+)+":\s*[_\w]+\([0-9]+\)\s*\}'
            pattern = r'=\{.*?\}'
            # 查找匹配项
            match = re.search(pattern,text,re.S)
            if match:
                matche_05 = match.group(0).replace("=","")
            else:
                matche_05 = re.search(r'\{"(.*?)}', text, re.S)
            try:
                str_code1 = str_code + "return " + matche_05 + "};}"
                res = execjs.compile(str_code1).call("get_param")
            except:
                str_code2 = str_code + "return " + matche_05 + "}"
                res = execjs.compile(str_code2).call("get_param")
            else:
                str_code3 = str_code + "return " + matche_05 + "};"
                res = execjs.compile(str_code3).call("get_param")
            return {"head":head,"par_param": res,"content":response.text}

        def Composite_parameter(lot,lotRes,lotNumber):
            key=list(lot.keys())[0]
            print(key)
            def split_lot_number(lot,lotNumber):
                result = []
                split_numbers = []
                for sublist in lot[key]:
                    temp = []
                    for num in sublist[key]:
                        if isinstance(num, list):
                            temp.append([x + 1 for x in num])
                        else:
                            temp.append(num[key])
                    result.append(temp)
                for sublist in result:
                    temp = ""
                    for num in sublist:
                        if len(num) > 1:
                            num[-1] += 1
                            temp += lotNumber[num[0]:num[1]]
                        else:
                            temp += lotNumber[num[0]]
                    split_numbers.append(temp)
                return split_numbers
            res1 = split_lot_number(lot, lotNumber)
            res2 = split_lot_number(lotRes, lotNumber)
            return {res1[0]: {res1[1]:res2[0]}}

        data=get_1()
        par=re_jscodeV1(data)
        with open("mapToDict.js",encoding="utf-8")as file:
            ctx=file.read()
        result=execjs.compile(ctx).call("v",par["keys"])
        print(result)
        print(par["paramsList"])
        res=Composite_parameter(result["lot"], result["lotRes"], par["paramsList"]["lot_number"])
        print(res)
        codehash=hashlib.md5(par["content"].encode("utf-8")).hexdigest()
        return {"head":par["head"],"md5":codehash,"params":par["par_param"],"keys":par["keys"]}


if __name__ == "__main__":
        b_time=datetime.now()
        # 格式化为“年-月-日 时:分:秒”
        formatted_time = b_time.strftime("%Y-%m-%d %H:%M:%S")
        for i in range(100):
                current_time = datetime.now()
                # 格式化为“年-月-日 时:分:秒”
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                jycode_veryity=get_jy_gcaptcha4Code()
                jycode_veryity["time"]=formatted_time
                print(jycode_veryity)
                is_same=conn.sadd("test",jycode_veryity["head"])
                if is_same:
                        conn.sadd("session", json.dumps(jycode_veryity))
                        logger.error("变化相差:{} min".format((current_time-b_time)/3600),jycode_veryity["md5"])
                time.sleep(10)
