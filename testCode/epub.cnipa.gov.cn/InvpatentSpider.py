import threading
import httpx
import aiohttp
import requests
import retrying
from loguru import logger
from lxml import etree
import re
import execjs
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from pymongo import ASCENDING, MongoClient, errors
from MQitems.PikaUse import SendMQ
from config import checkconfig,filtermap
from redis.client import Redis


session = requests.session()

headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://epub.cnipa.gov.cn",
        "Pragma": "no-cache",
        "Referer": "http://epub.cnipa.gov.cn/Dxb/IndexQuery",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    }


def demo2():
    url = "http://epub.cnipa.gov.cn/z5gPWiiwO6ht/2HA1rNA9S1Ml.b4c45da.js"
    response = session.get(url, headers=headers,verify=False)
    return response.text


def demo():
    url = "http://epub.cnipa.gov.cn/Dxb/IndexQuery"
    data = {
        "indexSearchModel.searchStr": "阿里巴巴",
        "indexSearchModel.fmgb": "false",
        "indexSearchModel.fmsq": "false",
        "indexSearchModel.xxsq": "false",
        "indexSearchModel.wgsq": "false",
        "__RequestVerificationToken": "CfDJ8MgwTdciqAVBk5rW9JE5mhqqyQIfAkv6V_GdBcNQkN2U1-7wDaxtlp1sQoc8kIPE8aRwPEsqZEAz0Ra5tVbZgc7j23HdOUBbYOdFuNKCfD6Glzk0ApTJ61Oz5s4LC744SA8IZ_O7WKsspSGxAL7quK0"
    }
    response =session.post(url, headers=headers,  data=data, verify=False)
    functo_code=demo2()
    html=etree.HTML(response.text)
    ts_code=html.xpath('//script[@r="m"]/text()')[0]
    meta_content=html.xpath('//meta[@r="m"]/@content')[0]
    Token=html.xpath('//input[@name="__RequestVerificationToken"]/@value')[0]
    js_code = open('rs6.js', encoding='utf-8').read()
    js = execjs.compile(js_code.replace("'ts_code'", ts_code).replace('content_code', meta_content).replace("'functo_code'", functo_code))
    ctx=js.call('get_cookie')
    session.cookies.set(ctx.split('=')[0],ctx.split('=')[1])
    return Token


class Test1():

    def __init__(self, area):
        self.config = checkconfig(area)
        filterAddr=filtermap(area)
        self.page = 2
        self.base_url = "http://epub.cnipa.gov.cn/Dxb/PageQuery"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        }
        self.local_conn = Redis("192.168.5.%s" % self.config["fAddr"][0],
                                self.config["fAddr"][1],
                                self.config["fAddr"][2],
                                self.config["fAddr"][3],
                                socket_connect_timeout=1170)
        self.client_01 = MongoClient(host="139.9.70.%s" % self.config["servSAddr"][0],
                                     port=self.config["servSAddr"][1],
                                     username=self.config["servSAddr"][2],
                                     password=self.config["servSAddr"][3],
                                     authSource=self.config["servSAddr"][4])
        self.serv_client = MongoClient(host="192.168.5.%s" % self.config[filterAddr][0],
                                       port=self.config[filterAddr][1],
                                       username=self.config[filterAddr][2],
                                       password=self.config[filterAddr][3],
                                       authSource=self.config[filterAddr][4])
        self.client = MongoClient("192.168.5.%s" % self.config['localSAddr'][0],self.config['localSAddr'][1])
        self.zlxx_item = list()

        self.cli_1 = self.client[self.config["rkey"]]["zlxx"]
        self.coll_3 = self.client_01[self.config["rkey"]]["专利"]
        self.zlxx_filter_fail = self.config["rkey"] + ":filter:zlxx_com"

        self.zlxx_filter_key = self.serv_client[self.config["rkey"]]["filter_zlxx_com"]
        self.zlxx_filter_key.create_index([('company', ASCENDING)], unique=True)

        self.coll_3_1 = self.client_01[self.config["rkey"]]["fails_专利"]
        self.coll_3_1.create_index([("propertyNum", ASCENDING)], unique=True)

        self.area_key = self.config["rkey"] + ":filter:company_id"
        self.comp_key = self.config["rkey"] + ":compList"
        self.processed_ids = set()  # 处理过的公司ID集合
        self.thread_local = threading.local()

    @retrying.retry(wait_fixed=5)
    def fetch_page(self, company, page):
        plist = {
            "发明授权": {"searchCatalogInfo.Pubtype": "3"},
            "发明公布": {"searchCatalogInfo.Pubtype": "1"},
            "发明授权更正": {"searchCatalogInfo.Pubtype": "4"},
            "实用新型": {"searchCatalogInfo.Pubtype": "6"},
            "外观设计": {"searchCatalogInfo.Pubtype": "9"},
            "外观设计更正": {"searchCatalogInfo.Pubtype": "10"},
        }
        """请求单页数据"""
        base_data = {
            "searchCatalogInfo.Ggr_Begin": "",
            "searchCatalogInfo.Ggr_End": "",
            "searchCatalogInfo.Pd_Begin": "",
            "searchCatalogInfo.Pd_End": "",
            "searchCatalogInfo.An": "",
            "searchCatalogInfo.Pn": "",
            "searchCatalogInfo.Ad_Begin": "",
            "searchCatalogInfo.Ad_End": "",
            "searchCatalogInfo.E71_73": company,
            "searchCatalogInfo.E72": company,
            "searchCatalogInfo.Edz": company,
            "searchCatalogInfo.E51": "",
            "searchCatalogInfo.Ti": company,
            "searchCatalogInfo.Abs": company,
            "searchCatalogInfo.Edl": company,
            "searchCatalogInfo.E74": company,
            "searchCatalogInfo.E30": "",
            "searchCatalogInfo.E66": "",
            "searchCatalogInfo.E62": "",
            "searchCatalogInfo.E83": "",
            "searchCatalogInfo.E85": "",
            "searchCatalogInfo.E86": "",
            "searchCatalogInfo.E87": "",
            "pageModel.pageNum": page,
            "pageModel.pageSize": "10",
            "sortFiled": "ggr_desc",
            "searchAfter": "",
            "showModel": "1",
            "isOr": "True",
        }
        # 添加处理过的专利号集合进行去重
        if not hasattr(self, 'processed_patents'):
            self.processed_patents = set()

        for param in plist.keys():
            # 每次循环创建新的data字典，避免参数累加
            data = base_data.copy()
            data.update(plist[param])
            try:
                response = requests.post(self.base_url, headers=self.headers, data=data, verify=False, timeout=(5, 25))
            except requests.Timeout as e:
                print(e)
                raise "超时"
            if response.status_code == 200 and "抱歉，没有您要查询的结果！" not in response.text:
                html = etree.HTML(response.text)
                jscode = html.xpath('//script[@type="text/javascript"]/text()')[0]
                config = re.findall('var obj_2 = (.*?);', jscode, re.S)[0]
                code = execjs.eval(config)
                total_items = int(code['total_item'])
                self.page = total_items  # 更新总页数
                self.parse_page(param, html)
            else:
                print(f"{company}:没有 {param} 专利项目！！")
                continue

    def saveDate(self, item):
        try:
            self.cli_1.insert_one(item)
            print("-----------【%s】保存本地数据库成功！！" % item["relationCompanyName"])
        except Exception as e:
            print("-----------!!!【%s】保存本地失败：" % item["relationCompanyName"], e)
        try:
            self.coll_3.insert_one(item)
            print("-----------【%s】保存服务器数据库成功！！" % item["relationCompanyName"])
        except Exception as e:
            print("-----------!!!【%s】保存服务器失败：" % item["relationCompanyName"], e)
        # self.local_conn.lrem(self.comp_key, 1, company)

    def parse_page(self, type, html):
        reExp = {
            "发明授权": ["dl[7]", "dl[8]", "dl[3]"],
            "发明公布": ["dl[5]", "dl[6]", "dl[3]"],
            "发明授权更正": ["dl[6]", "dl[7]", "dl[4]"],
            "实用新型": ["dl[5]", "dl[6]", "dl[3]"],
            "外观设计": ["dl[5]", "dl[6]", "dl[3]"],
            "外观设计更正": ["dl[6]", "dl[7]", "dl[4]"]
        }
        """解析单页数据"""
        items = html.xpath("//div[@class='item']")
        infoStatus = str(html.xpath("//div[@class='func']/a/text()")[0]).split()
        for info in items:
            item = dict()
            item["propertyType"] = "专利"
            item["propertyTitle"] = str(info.xpath("./h1/text()")[0]).strip()
            item["zlOpenNum"] = str(info.xpath("./div[@class='info']/dl[1]/dd/text()")[0]).strip()
            item["filingDate"] = str(info.xpath("./div[@class='info']/dl[4]/dd/text()")[0]).strip()
            item["gainDate"] = str(info.xpath("./div[@class='info']/dl[2]/dd/text()")[0]).strip()
            item["infoType"] = type
            item["infoStatus"] = infoStatus[0]
            item["relationCompanyName"] = str(info.xpath(f"./div[@class='info']/{reExp[type][0]}/dd/text()")[0]).strip()
            item["zlInventor"] = str(info.xpath(f"./div[@class='info']/{reExp[type][1]}/dd/text()")[0]).strip()
            item["propertyNum"] = str(info.xpath("./div[@class='info']/dl[3]/dd/text()")[0]).strip()

            # 添加去重逻辑
            if item["propertyNum"] in self.processed_patents:
                print(f"跳过重复专利: {item['propertyNum']}")
                continue

            self.processed_patents.add(item["propertyNum"])

            try:
                self.send_data(item)
            except Exception as e:
                print("【！！】发送服务器失败！！", e)
            print(item)
            self.saveDate(item)
            del item["_id"]

    def spider(self, company):
        page = 1
        total_pages = 1  # 初始总页数
        max_workers = 10  # 最大线程数
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while page <= total_pages:
                futures = []
                # 动态调整线程数，确保不超过总页数
                current_workers = min(max_workers, total_pages - page + 1)
                for _ in range(current_workers):
                    future = executor.submit(self.fetch_page, company, page)
                    futures.append(future)
                    page += 1
                # 处理已完成的任务
                for future in as_completed(futures):
                    future.result()
                    # 更新总页数
                    total_pages = self.page

    def send_data(self, item):
        # if "_id" in item:
        #     del item["_id"]
        print("记录打点:", len(self.zlxx_item))
        self.zlxx_item.append(item)
        if len(self.zlxx_item) >= 10:
            SendMQ().mongoToMQ(4, self.zlxx_item)
            print(f"【*】发送成功：{self.zlxx_item}")
            self.zlxx_item.clear()

    def _pushcom(self, comp):
        self.local_conn.lpush(self.comp_key, comp.decode())


    def copydata(self,executor):
        if not self.local_conn.exists(self.comp_key):
            num = self.local_conn.scard(self.area_key)
            print("找到: 【", num, "】 个文档！！")
            comps = self.local_conn.smembers(self.area_key)
            futures = []
            _ = 1
            for comp in tqdm(comps, desc="处理进度", leave=True):
                self.local_conn.lpush(self.comp_key, comp.decode())
                futures.append(executor.submit(self._pushcom, comp))
                _ += 1
            for future in as_completed(futures):
                future.result()
            print(f"=========实际：{num}，成功导入【{_}】公司成功！！")

    def main(self):
        with ThreadPoolExecutor(max_workers=3) as executor:
            self.copydata(executor)
            flist = []
            _ = 0
            processed_companies = set()  # 用于记录已处理的公司

            while True:
                comp = self.local_conn.lpop(self.comp_key)
                if not comp:
                    break  # 如果没有更多公司，退出循环
                comp_name = comp.decode()
                try:
                    self.zlxx_filter_key.insert_one({"company": comp_name})
                    if comp_name in processed_companies:
                        continue  # 如果公司已经处理过，跳过
                    print(comp_name)
                    self.processed_ids.add(comp_name)
                    processed_companies.add(comp_name)  # 记录已处理的公司
                    flist.append(executor.submit(self.spider, comp_name))
                    _ += 1
                    if len(flist) >= 5:
                        for future in as_completed(flist):
                            future.result()
                        flist.clear()  # 清空已完成的任务列表
                    print(f"这是第 【{_}】 家公司！！")
                except errors.DuplicateKeyError:
                    logger.warning(f"【*】专利已过滤:{comp_name}")

            for future in flist:
                future.result()


class Test2():

    def __init__(self):
        self.page = 2

    async def demo1(self, page):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        }
        url = "http://epub.cnipa.gov.cn/Dxb/PageQuery"
        data = {
            "searchCatalogInfo.Pubtype": "1",
            "searchCatalogInfo.Ggr_Begin": "",
            "searchCatalogInfo.Ggr_End": "",
            "searchCatalogInfo.Pd_Begin": "",
            "searchCatalogInfo.Pd_End": "",
            "searchCatalogInfo.An": "",
            "searchCatalogInfo.Pn": "",
            "searchCatalogInfo.Ad_Begin": "",
            "searchCatalogInfo.Ad_End": "",
            "searchCatalogInfo.E71_73": "阿里巴巴",
            "searchCatalogInfo.E72": "阿里巴巴",
            "searchCatalogInfo.Edz": "阿里巴巴",
            "searchCatalogInfo.E51": "",
            "searchCatalogInfo.Ti": "阿里巴巴",
            "searchCatalogInfo.Abs": "阿里巴巴",
            "searchCatalogInfo.Edl": "阿里巴巴",
            "searchCatalogInfo.E74": "阿里巴巴",
            "searchCatalogInfo.E30": "",
            "searchCatalogInfo.E66": "",
            "searchCatalogInfo.E62": "",
            "searchCatalogInfo.E83": "",
            "searchCatalogInfo.E85": "",
            "searchCatalogInfo.E86": "",
            "searchCatalogInfo.E87": "",
            "pageModel.pageNum": page,
            "pageModel.pageSize": "10",
            "sortFiled": "ggr_desc",
            "searchAfter": "",
            "showModel": "1",
            "isOr": "True",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data, ssl=False) as response:
                html_text = await response.text()
                html = etree.HTML(html_text)
                jscode = html.xpath('//script[@type="text/javascript"]/text()')[0]
                config = re.findall('var obj_2 = (.*?);', jscode, re.S)[0]
                print(config)
                code = execjs.eval(config)
                self.page = int(code['total_item'])
                print(self.page)
                if page > self.page:
                    return None
                return html

    def demo3(self, html):
        items = html.xpath("//div[@class='item']")
        for item in items:
            title = item.xpath("./h1/text()")[0]
            print(str(title).strip())

    async def main(self):
        page = 1
        while True:
            result = await self.demo1(page)
            # 明确判断 result 是否为 None
            if result is None:
                break
            # 检查 result 是否有子节点
            if len(result) == 0:
                break
            self.demo3(result)
            page += 1



if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(Test2().main())
    Test1("fujian").main()


