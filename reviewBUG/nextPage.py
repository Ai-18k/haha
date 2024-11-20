# _*_ coding:UTF-8 _*

from concurrent.futures import ThreadPoolExecutor
import threading
import random
import logging
import json
import time
from retrying import retry

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置文件路径
PROGRESS_FILE = 'progress.json'


def save_progress(page):
    """保存当前页面进度到文件"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({'page': page}, f)


def load_progress():
    """加载保存的页面进度"""
    try:
        with open(PROGRESS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('page', 1)
    except FileNotFoundError:
        return 1


@retry(wait_fixed=1000)  # 1秒的重试间隔
def demo1(page):
    try:
        print(page)
        ee = int(random.random() * page)
        if ee < 1:
            save_progress(page)
            raise SyntaxError("刷新")
        logger.info("这是第%d页" % page)
    except SyntaxError as e:
        logger.error(f"遇到错误: {e}")
        raise


# 创建一个线程局部存储对象
thread_local_data = threading.local()


def thread_function(thread_id):
    # 初始化线程局部数据
    thread_local_data.page = 0

    for _ in range(5):  # 每个线程循环5次
        # 更新线程局部数据
        thread_local_data.page += 1
        print(f"线程 {thread_id} 的页面: {thread_local_data.page}")
        time.sleep(random.uniform(0.1, 0.5))  # 模拟工作负载


def main():
    # current_page = load_progress()
    #
    # while True:
    #     try:
    #         demo1(current_page)
    #         # 保存进度
    #         current_page += 1.txt
    #         time.sleep(1.txt)  # 设置合适的请求间隔，避免对服务器造成过大负担
    #     except Exception as e:
    #         logger.error(f"运行出错: {e}")
    #         # 在这里选择是继续尝试还是退出程序
    #         break
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(thread_function, i) for i in range(30)]
        # 等待所有线程完成
        for future in futures.as_completed(futures):
            try:
                future.result()  # 获取线程执行结果
            except Exception as e:
                print(f"线程执行出错: {e}")


if __name__ == "__main__":
    main()
