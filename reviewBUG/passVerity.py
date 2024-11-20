import base64
import io
import os
import re
import cv2
import ddddocr
import execjs
import requests
from loguru import logger
from lxml import etree
import json
import uuid
from FunComponent.AccountDetection import ImageProcess
import requests
from retrying import retry

# html=open("1.txt","r",encoding="utf-8").read()
# script=open("jscode.txt","r",encoding="utf-8").read()
# print(html)
def get_span(pageinfo):
    html = etree.HTML(pageinfo)
    script = html.xpath("//body//script[1]/text()")[0]
    # print(script)
    current_path = os.path.dirname(__file__)
    # print(current_path)
    jscode = open("../RiskcontrolPass/jscode/ast_decode.js", encoding="utf-8").read()
    span_par = execjs.compile(jscode).call("cc", script)
    logger.info(span_par)


class CC:
    def PostPic(self,final_image):
        out_buff=io.BytesIO()
        final_image.save(out_buff, format='PNG')
        byte_pic=out_buff.getvalue()
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "DNT": "1",
            "Origin": "http://192.168.5.181:8011",
            "Pragma": "no-cache",
            "Referer": "http://192.168.5.181:8011/char1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        url = "http://192.168.5.181:8011/dianxuan/identify"
        data = {
            "dataType": 2,
            "imageSource": base64.b64encode(byte_pic).decode('utf-8'),
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            data=response.json()
            _crop=data["data"]["res"]["crop_centre"]
            return _crop
        else:
           raise Exception("链接失效")



retry(wait_fixed=1000)
def verify(content):
    url = "http://api.jfbym.com/api/YmServer/customApi"
    data = {
        ## 关于参数,一般来说有3个;不同类型id可能有不同的参数个数和参数名,找客服获取
        "token": "UquqP253oi04KuvBMFYVmRcx_1lJl7Q1FxIwknR9IpU",
        "type": "30114",
        "image": base64.b64encode(content).decode(),
        "extra":"je4_phrase"
    }
    _headers = {
        "Content-Type": "application/json"
    }
    response = requests.request("POST", url, headers=_headers, json=data)
    print(response)
    if response.status_code==200:
        data=response.json()
        x_coord = data["data"]["data"]
        xy = [str(i).split(",") for i in str(x_coord).split("|")]
        result = [[int(x) for x in sublist] for sublist in xy]
        return result
    else:
        raise Exception("识别失败")

ocr = ddddocr.DdddOcr(det=False, ocr=False,show_ad=False)
ocr1 = ddddocr.DdddOcr(beta=True,show_ad=False)  # 切换为第二套ocr模型
ocr2 = ddddocr.DdddOcr(det=True,show_ad=False)

class Demo:

    def __init__(self,Reqest,session):
        self.session=session
        self.Reqest=Reqest
        # self.Reqest['captcha_id'] = captcha_id
        logger.info(self.Reqest)

    def ocr_img(self,img, filepath):
        with open(img, 'rb') as f:
            image = f.read()
        bboxes = ocr2.detection(image)
        # print(bboxes)
        im = cv2.imread(img)
        for bbox in bboxes:
            x1, y1, x2, y2 = bbox
            im = cv2.rectangle(im, (x1, y1), (x2, y2), color=(0, 0, 255), thickness=2)
        cv2.imwrite(filepath + "/click_img_new.jpg", im)


    def download_img(self,imgs, filename, type, uuid):
        dir_path = f"E:/AIProject/Datesets/imgs/{type}/{uuid}"
        file_path = os.path.join(dir_path, filename + ".png")
        # 如果文件夹不存在则创建
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if type == "phrase":
            with open(file_path, 'wb') as f:
                f.write(imgs)
        elif type == "icon":
            with open(file_path, 'wb') as f:
                f.write(imgs)
            if filename == "click_img":
                self.ocr_img(file_path, dir_path)


    def get_1(self):
        # try:
        headers = {
            "Host": "gcaptcha4.geetest.com",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
            "DNT": "1",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": self.Reqest["ua"],
            "sec-ch-ua-platform": "\"Windows\"",
            "Accept": "*/*",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "script",
            "Referer": "https://www.tianyancha.com/",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        _uuid=uuid.uuid1()
        url = "https://gcaptcha4.geetest.com/load"
        params = {
            "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
            "challenge": _uuid,
            # "challenge": "09d9c310-e098-467a-8b6c-c61ae6642e3c",
            "client_type": "web",
            "lang": "zho"
        }
        response = self.session.get(url, headers=headers, params=params)
        if response.status_code == 200:
            cookies = response.cookies.get("captcha_v4_user")
            res = json.loads(response.text.strip("(").strip(")"))
            # print(res)
            type = res["data"]['captcha_type']
            lot_number = res.get("data").get("lot_number")
            process_token = res.get("data").get("process_token")
            pow_detail = res.get("data").get("pow_detail")
            pow_detail = [pow_detail[i] for i in pow_detail if isinstance(pow_detail, dict)]
            payload = res.get("data").get("payload")
            static_path = res.get("data").get("static_path")
            params_list = {
                "captcha_id": "af29b3003fc94f2ba29e865b31ee86ee",
                "lot_number": lot_number,
                "process_token": process_token,
                "pow_detail": pow_detail,
                "payload": payload,
                "cookies": cookies,
                "static_path": static_path
            }
            uuid1 = uuid.uuid1()
            if type =="icon":
                print(">>>>>>>>>>>>>>>>>>>>>图形验证>>>>>>>>>>>>>>")
                q_list = res["data"]['ques']
                bytes_list = []
                for index, img_url in enumerate(q_list):
                    tag = requests.get("https://static.geetest.com/" + img_url).content
                    self.download_img(tag, str(index), type, uuid1)
                    word_pic = ImageProcess.wordprocess(tag)
                    bytes_list.append(word_pic)
                imgs_url = "https://static.geetest.com/" + res["data"]['imgs']
                slide_bytes = requests.get(imgs_url).content
                new_pic = ImageProcess.mergePic(slide_bytes, bytes_list)
                click_list = CC().PostPic(new_pic)
                click_smark = []
                for _word in click_list:
                    click_smark.append([round(int(_word[0]) * 100 / 3), round(int(_word[1]) * 50)])
                logger.info(click_smark)
                self.download_img(slide_bytes, "click_img", type, uuid1)
                params_list["smark"] = click_smark
                params_list["type"] = "icon"
            elif type == "phrase":
                print(">>>>>>>>>>>>>>>>>>>>>>语序验证>>>>>>>>>>>>>>")
                bg_url = "https://static.geetest.com/" + res["data"]['imgs']
                bg_bytes = requests.get(bg_url).content
                self.download_img(bg_bytes, "bg_img", type, uuid1)
                click_list=verify(bg_bytes)
                click_smark=[]
                for _word in click_list:
                    click_smark.append([round(int(_word[0]) * 100 / 3), round(int(_word[1]) * 50)])
                logger.info(click_smark)
                params_list["smark"] = click_smark
                params_list["type"] = "phrase"
            return params_list


    def re_js_code(self):
        params_list = self.get_1()
        headers = {
            "Host": "static.geetest.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google "
                         "Chrome\";v=\"114\"",
            "origin": "https://www.tianyancha.com",
            "dnt": "1",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": self.Reqest["ua"],
            "sec-ch-ua-platform": "\"Windows\"",
            "accept": "*/*",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "script",
            "referer": "https://www.tianyancha.com/",
            "accept-language": "zh-CN,zh;q=0.9"
        }
        url = "https://static.geetest.com" + params_list["static_path"] + "/js/gcaptcha4.js"
        response = self.session.get(url,headers=headers)
        str_code = ""
        match = re.search(r'(.*?)\.', response.text, re.S)
        head = match.group().strip(".")
        matche_01 = re.findall(rf"{head}\..*?\}}\(\);", response.text, re.S)
        str_code += matche_01[0] + matche_01[1]
        matche_02 = re.findall(rf'{head}\..*?}};', response.text, re.S)
        str_code += matche_02[2] + matche_02[3] + f"function {head}() {{}};"
        matche_03 = re.search(r"!function\(\){var.*?};}\(\),", response.text, re.S)
        text = matche_03.group()
        matche_04 = re.search(r"var.*?};", text, re.S)
        str_code += "function get_param(){" + matche_04.group()
        matche_05 = re.search(r'\{".*?}};', text, re.S)
        str_code += "return " + matche_05.group() + "};"
        res = execjs.compile(str_code).call("get_param")
        return {"par_param": res, "par_data": params_list}


    def get_2(self):
        try:
            headers = {
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "DNT": "1",
                "Pragma": "no-cache",
                "Referer": "https://www.tianyancha.com/",
                "Sec-Fetch-Dest": "script",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site",
                "User-Agent": self.Reqest["ua"],
                "sec-ch-ua": "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", "
                             "\"Chromium\";v=\"123\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\""
            }
            url = "https://gcaptcha4.geetest.com/verify"
            res = self.re_js_code()
            with open("3.js", encoding="utf-8") as f:
                jscode =f.read()
            data = execjs.compile(jscode).call("_fff", res["par_data"], res["par_param"])
            params = {
                "captcha_id": res["par_data"]["captcha_id"],
                "client_type": "web",
                "lot_number": res["par_data"]["lot_number"],
                "payload": res["par_data"]["payload"],
                "process_token": res["par_data"]["process_token"],
                "payload_protocol": "1",
                "pt": "1",
                "w": data["res"]
            }
            response = self.session.get(url,headers=headers,params=params)
            if response.status_code == 200:
                resp = json.loads(str(response.text).strip("(").strip(")"))
                gen_time = resp["data"]["seccode"]["gen_time"]
                captcha_output =resp["data"]["seccode"]["captcha_output"]
                captcha_id =resp["data"]["seccode"]["captcha_id"]
                lot_number = resp["data"]["seccode"]["lot_number"]
                pass_token = resp["data"]["seccode"]["pass_token"]
                params_list1 = {
                    "captcha_id": captcha_id,
                    "lot_number": lot_number,
                    "pass_token": pass_token,
                    "gen_time": gen_time,
                    "captcha_output": captcha_output,
                    "pow_sign": data["pow_sign"], }
                return params_list1
            else:
                logger.error(f"请求状态码:{response.status_code}")
        except Exception as e:
            logger.error("验证滑块异常:{}".format(e))


    # @retry(stop_max_attempt_number=5, wait_fixed=1000)
    def passVerity(self,sign):
        par=self.get_2()
        with open("4.js", encoding="utf-8") as f:
            jscode =f.read()
        IfMatch = execjs.compile(jscode).call("_fff",par["lot_number"], sign)
        headers={
            "Host": "www.tianyancha.com",
            "Cache-Control": "max-age=0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
            "If-Match": f"{IfMatch}",
            "sec-ch-ua-mobile": "?0",
            "X-Requested-With": "XMLHttpRequest",
            # "User-Agent": self.Reqest["ua"],
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "DNT": "1",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": "https://www.tianyancha.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.tianyancha.com/advance/search/e-pc_searchinfo",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        # cookies = {
        #     "TYCID": "ee77dec089d411efad3b8d5e84c839bd",
        #     "ssuid": "642228600",
        #     "sajssdk_2015_cross_new_user": "1",
        #     "_ga": "GA1.2.1230606725.1728873318",
        #     "_gid": "GA1.2.2037681351.1728873318",
        #     "CUID": "66a0445cccf32c4e251bce9c3efa23e6",
        #     "searchSessionId": "1728873813.89647002",
        #     "HWWAFSESID": "ecb3cdcde7affdb1cc",
        #     "HWWAFSESTIME": "1728919644447",
        #     "jsid": "SEO-BING-ALL-SY-000001",
        #     "csrfToken": "A5RtfCgkkJY2alSFRHkwVGdO",
        #     "bannerFlag": "true",
        #     "Hm_lvt_e92c8d65d92d534b0fc290df538b4758": "1728873317,1728919649",
        #     "Hm_lpvt_e92c8d65d92d534b0fc290df538b4758": "1728919649",
        #     "HMACCOUNT": "48DADAF5EBAB5424",
        #     "sensorsdata2015jssdkcross": "%7B%22distinct_id%22%3A%22285987829%22%2C%22first_id%22%3A%2219288e13d7345-02f1523e3a033b2-26001051-1049088-19288e13d743ec%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fcn.bing.com%2F%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTkyODhlMTNkNzM0NS0wMmYxNTIzZTNhMDMzYjItMjYwMDEwNTEtMTA0OTA4OC0xOTI4OGUxM2Q3NDNlYyIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjI4NTk4NzgyOSJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22285987829%22%7D%2C%22%24device_id%22%3A%2219288e13d7345-02f1523e3a033b2-26001051-1049088-19288e13d743ec%22%7D",
        #     "tyc-user-info": "{%22state%22:%224%22%2C%22vipManager%22:%220%22%2C%22mobile%22:%2213020737097%22%2C%22userId%22:%22285987829%22%2C%22isExpired%22:%220%22}",
        #     "tyc-user-info-save-time": "1728920180731",
        #     "auth_token": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxMzAyMDczNzA5NyIsImlhdCI6MTcyODkyMDE4MCwiZXhwIjoxNzMxNTEyMTgwfQ.M2evkHypaHmsYRTyCGvhn_c2uYv4exHSQMLq0mjgP3bnuLK0LzcKjyRW1f2Sd_A7x9MLZwxOiDRfRC-ywVcsnQ",
        #     "tyc-user-phone": "%255B%252213020737097%2522%255D"
        # }
        url = "https://www.tianyancha.com/sorry/verifyCaptcha4.json"
        data = {
            "captcha_id":"af29b3003fc94f2ba29e865b31ee86ee",
            "lot_number": par["lot_number"],
            "pass_token":par["pass_token"],
            "gen_time": par["gen_time"],
            "captcha_output":par["captcha_output"],
        }
        data = json.dumps(data, separators=(',', ':'))
        response = self.session.post(url, headers=headers,data=data)
        if response.status_code==200:
            if response.json()["state"]=="ok":
                return True
            else:
                logger.error(f"验证失败！响应:{response.json()}")
                raise Exception("验证失败！重试")
        else:
            logger.error("{}：状态异常！！".format(response.status_code))
            raise Exception("验证失败！重试")




