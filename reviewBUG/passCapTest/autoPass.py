#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :autoPass.py
# @Time      :2024/11/5 9:03
# @Author    : 18k
import base64
import json
import re
import sys
import os
import time
import urllib
import requests
from loguru import logger
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)
# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)

from selenium import webdriver


class CC:
    def PostPic(self, pic_list):
        tmp = str(time.time())
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        }
        url = "http://192.168.5.181:10121/geetest4_icon/gradio_api/queue/"
        # url = "http://127.0.0.1:1012/geetest4_icon/gradio_api/queue/"
        params = {"": ""}
        data = {
            "data": pic_list,
            "event_data": None,
            "fn_index": 1,
            "trigger_id": 121,
            "session_hash": tmp
        }
        data = json.dumps(data, separators=(',', ':'))
        requests.post(url + "join", headers=headers, params=params, data=data, verify=False)
        param = {
            "session_hash": tmp
        }
        time.sleep(0.1)
        response = requests.get(url + "data", headers=headers, params=param, verify=False)
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


def click_verify(driver,plan):
    # [[42.5, 45.5], [197.5, 46.5], [208.5, 114.0]]
    xpath = "//*[(text()='请在下图依次点击')]/../../following-sibling::div/div/div/div[1]/div[1]"
    bg_tag = driver.find_element(By.XPATH, xpath)
    for crop in plan:
        print(crop)
        x = int(crop[0]) - int(bg_tag.size['width'] / 2)
        y = int(crop[1]) - int(bg_tag.size['height'] / 2)
        ActionChains(driver).move_to_element_with_offset(bg_tag, xoffset=x, yoffset=y).click().perform()
        time.sleep(0.5)
    driver.find_element(By.XPATH, "//*[(text()='确定')]").click()
    return True

def Imageprocess(flg,url_list):
    if flg=="icon":
        pic_list=[]
        for url in url_list:
            pic=requests.get(url).content
            base_pic=base64.b64encode(pic).decode("utf-8")
            pic_list.append(base_pic)
        # return {flg:pic_list}
        return pic_list
    elif flg=="phrase":
        bg=requests.get(url_list[0]).content
        # return {flg:base64.b64encode(bg).decode("utf-8")}
        return bg

def fetch_phrase(driver):
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>语序验证<<<<<<<<<<<<<<<<<<<<<<<<")
    xpath = "//*[(text()='请按语序依次点击')]/../../following-sibling::div/div/div/div[1]/div[1]"
    p_element = driver.find_element(By.XPATH, xpath)
    style_value = p_element.get_attribute("style")
    # url=re.findall('\("(.*)"\);',style_value,re.S)[0]
    bg_link = re.search('https(.*).jpg', style_value, re.S).group()
    print(bg_link)
    Imageprocess("phrase", bg_link)

def fetch_icon(driver):
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>图形验证<<<<<<<<<<<<<<<<<<<<<<<<")
    tag1_xpath = "//*[(text()='请在下图依次点击')]/following-sibling::div/img[1]"
    tag2_xpath = "//*[(text()='请在下图依次点击')]/following-sibling::div/img[2]"
    tag3_xpath = "//*[(text()='请在下图依次点击')]/following-sibling::div/img[3]"
    bg_xpath = "//*[(text()='请在下图依次点击')]/../../following-sibling::div/div/div/div[1]/div[1]"
    tag1_element = driver.find_element(By.XPATH, tag1_xpath)
    tag2_element = driver.find_element(By.XPATH, tag2_xpath)
    tag3_element = driver.find_element(By.XPATH, tag3_xpath)
    bg_element = driver.find_element(By.XPATH, bg_xpath)
    pic_link1 = tag1_element.get_attribute("src")
    pic_link2 = tag2_element.get_attribute("src")
    pic_link3 = tag3_element.get_attribute("src")
    style_value = bg_element.get_attribute("style")
    print(pic_link1)
    print(pic_link2)
    print(pic_link3)
    # bg_link = re.findall('\("(.*)"\);', bg_link, re.S)[0]
    bg_link = re.search('https(.*).jpg', style_value, re.S).group()
    print(bg_link)
    return Imageprocess("icon", [bg_link,pic_link1,pic_link2,pic_link3])


def init(hearders):
    chrome_options = Options()
    # 设置请求头信息
    chrome_options.add_experimental_option('prefs', hearders)
    # chrome_options.add_argument("--headless")  # 启用无头模式
    chrome_options.add_experimental_option('excludeSwitches',['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features")
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.add_argument('user-agent=' + self.ua)
    # 保持窗口长久存活
    # chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # self.chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--ignore-certificate-errors')
    return webdriver.Chrome(options=chrome_options)


def main(cookie,hearders):
    # 访问目标网站
    driver=init(hearders)
    driver.set_window_size(200, 500)
    wait = WebDriverWait(driver, 30)
    driver.get("https://www.tianyancha.com/company/26120374")
    time.sleep(2)
    cookies=[{"name":i,"value":cookie[i],"domain":'www.tianyancha.com'} for i in cookie]
    # 添加 Cookies
    for cookie in cookies:
        driver.add_cookie(cookie)
    # 刷新页面以使 Cookies 生效
    driver.refresh()
    # 此时你应该已经携带了 Cookies，可以直接访问已经登录的网页
    driver.get("https://www.tianyancha.com/company/26120374")  # 例如：进入个人主页

    # xpath ="//*[(text()='点击按钮开始验证')]"
    # wait.until(EC.presence_of_element_located((By.XPATH, xpath))).click()

    time.sleep(2)
    driver.find_element(By.XPATH, "//div[@id='captcha']/div[3]").click()
    time.sleep(2)
    try:
        element=driver.find_element(By.XPATH, "//*[(normalize-space(text())='请按语序依次点击')]")
    except:
        element=driver.find_element(By.XPATH, "//*[(normalize-space(text())='请在下图依次点击')]")

    if element.text=="请按语序依次点击":
        data=fetch_phrase(driver)
        driver.close()
        driver.quit()
        print(data)
        return False
    elif element.text=="请在下图依次点击":
        pic_list=fetch_icon(driver)
        plan=CC().PostPic(pic_list)
        # click_verify(driver,plan)
        xpath="//*[(text()='请在下图依次点击')]/../../following-sibling::div/div/div/div[1]/div[1]"
        bg_tag = driver.find_element(By.XPATH,xpath)
        for crop in plan:
            print(crop)
            x = int(crop[0]) - int(bg_tag.size['width'] / 2)
            y = int(crop[1]) - int(bg_tag.size['height'] / 2)
            ActionChains(driver).move_to_element_with_offset(bg_tag,xoffset=x,yoffset=y).click().perform()
            time.sleep(0.5)
        driver.find_element(By.XPATH, "//*[(text()='确定')]").click()
        time.sleep(3)
        driver.close()
        driver.quit()
        return True

if __name__ == '__main__':
    head={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "DNT": "1",
        "Pragma": "no-cache",
        "Referer": "https://www.tianyancha.com/company/26120374",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }
    cookies = {
        "ssuid": "8186459100",
        "HWWAFSESID": "8897712ab20463d6d90",
        "HWWAFSESTIME": "1730780177021",
        "csrfToken": "GOvBZq2kbodVjpyS4ryJtyCe",
        "TYCID": "b60805609b2c11ef9d8f439fefcae8e2",
        "tyc-user-info": "{%22state%22:%220%22%2C%22vipManager%22:%220%22%2C%22mobile%22:%2218721200865%22%2C%22userId%22:%2216694566%22}",
        "tyc-user-info-save-time": "1730780181044",
        "auth_token": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxODcyMTIwMDg2NSIsImlhdCI6MTczMDc4MDE4MCwiZXhwIjoxNzMzMzcyMTgwfQ.DFooLKT2g5wcnNWNC53VS2DW9MyY8M2JdyXSwGvkOkrWMWW_w4DSV-8XeifsKfkyEP4tDb9TTtvuOIZ8I3Dqqg",
        "tyc-user-phone": "%255B%252218721200865%2522%255D",
        "CUID": "b7d952fada392b75882c0038332e4190"
    }
    main(cookies,head)

