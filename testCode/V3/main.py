from concurrent.futures import ThreadPoolExecutor, as_completed
from gudongSpider import Gudong
from Business_info_spider import Currspider
from NoMemeryData import NoMemerySpider
from judicial_Business_spider import Hisspider
from JudModule import FLSS


def run_all_for_area(area):
    """
    同时运行五个参数（五个表/爬虫）任务
    """
    tasks = [
        lambda: Currspider(area).main(),
        lambda: NoMemerySpider(area).main(),
        lambda: Hisspider(area).main(),
        lambda: FLSS(area).run(),
        lambda: Gudong(area).main()
    ]
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_task = {executor.submit(task): idx for idx, task in enumerate(tasks)}
        for future in as_completed(future_to_task):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"Area: {area}, Task {future_to_task[future]} failed: {e}")
    return results


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
        # 外层线程池控制每个地区的五个任务并发
        with ThreadPoolExecutor(max_workers=10) as executor:
            area_futures = [executor.submit(run_all_for_area, area) for area in arealist]
            for future in as_completed(area_futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Area group failed: {e}")


if __name__ == '__main__':
    main()