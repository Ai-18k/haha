from concurrent.futures import ThreadPoolExecutor
from gudongSpider import Gudong
from Business_info_spider import Currspider
from NoMemeryData import NoMemerySpider
from judicial_Business_spider import Hisspider
from JudModule import FLSS

def main():
    with ThreadPoolExecutor(3) as f:
        arealist = [
            "chongqing",
            "fujian",
            "guizhou",
            "hubei",
            # "neimenggu",
            # "sanxi",
            # "shanghai",
            # "shanxi",
            # "xinjiang",
            # "zhejiang",
            # "sichuan",
            # "hunan",
            # "henan",
            # "guangdong",
            # "heilongjiang",
            # "qinghai",

            # "beijing",
            # "hainan",
            # "hebei",
            # "jiangsu",
            # "jiangxi",
            # "jilin",
            # "ningxia",
            # "shandong",
            # "xizang",
            # "liaoning",
            # "guangxi",
            # "anhui",
            # "yunnan",
            # "tianjin",
            # "gansu",
            # "taiwan",
            # "xianggang"
        ]
        future=[]
        future1=[]
        future2=[]
        future3=[]
        future4=[]
        for area in arealist:
            future.append(f.submit(Currspider(area).main))
            future1.append(f.submit(NoMemerySpider(area).main))
            future2.append(f.submit(Hisspider(area).main))
            future3.append(f.submit(FLSS(area).run))
            future4.append(f.submit(Gudong(area).main))
        for tasks in [future, future1, future2, future3, future4]:
            for task in tasks:
                task.result()

if __name__ == '__main__':
    main()