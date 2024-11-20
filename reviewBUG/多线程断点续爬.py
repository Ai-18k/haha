# _*_ coding:UTF-8 _*

import requests
import threading
import pickle
import os
import time

# 配置
BASE_URL = 'http://example.com/page='
START_PAGE = 1
END_PAGE = 10
THREAD_COUNT = 5
BREAKPOINT_FILE = 'breakpoint.pkl'


# 保存断点
def save_breakpoint(current_page):
    with open(BREAKPOINT_FILE, 'wb') as f:
        pickle.dump(current_page, f)


# 读取断点
def load_breakpoint():
    if os.path.exists(BREAKPOINT_FILE):
        with open(BREAKPOINT_FILE, 'rb') as f:
            return pickle.load(f)
    return START_PAGE


# 爬取页面
def fetch_page(page_num):
    try:
        response = requests.get(BASE_URL + str(page_num))
        response.raise_for_status()  # 检查请求是否成功
        # 这里可以处理响应内容，例如保存到文件或解析数据
        print(f"Fetched page {page_num}")
        # 假设我们处理的数据会导致断点保存
        save_breakpoint(page_num)
    except requests.RequestException as e:
        print(f"Failed to fetch page {page_num}: {e}")


# 工作线程函数
def worker(start_page, end_page):
    for page_num in range(start_page, end_page + 1):
        fetch_page(page_num)
        time.sleep(1)  # 模拟延迟


# 主函数
def main():
    start_page = load_breakpoint()
    print(f"Resuming from page {start_page}")

    # 分割任务
    pages_per_thread = (END_PAGE - start_page + 1) // THREAD_COUNT
    threads = []

    for i in range(THREAD_COUNT):
        thread_start_page = start_page + i * pages_per_thread
        if i == THREAD_COUNT - 1:
            thread_end_page = END_PAGE
        else:
            thread_end_page = thread_start_page + pages_per_thread - 1

        thread = threading.Thread(target=worker, args=(thread_start_page, thread_end_page))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()




















