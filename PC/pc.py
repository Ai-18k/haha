#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :pc.py
# @Time      :2024/12/21 23:48
# @Author    : 18k
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Project root:", PROJECT_ROOT)
# 将项目根目录添加到Python路径
sys.path.append(PROJECT_ROOT)

import re
import tkinter as tk
from tkinter import ttk
from redis import Redis

# 创建主窗口
root = tk.Tk()
root.title("下拉框界面")
root.geometry("700x500")

# 配置主窗口的行列权重，使其自适应大小
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# 创建标签和下拉框
options = []
for i in range(1, 5):
        options.append(" %d 号机" % i)

options1 = ["443", "8080", "7933", "7980", "8490", "14117", "27017"]

options2 = []
for i in range(17):
        options2.append(i)

# 机器号对应的IP地址映射
iprex = {
        # "1": "192.168.5.1",
        # "2": "192.168.5.2",
        # "3": "192.168.5.3",
        # "4": "192.168.5.4"
        "1": "127.0.0.1",
        "2": "127.0.0.1",
        "3": "127.0.0.1",
        "4": "127.0.0.1"
}

ip_list = list()


def update_values(i_combo, p_combo, db_combo, pwd_combo, value_dict):
        # 获取机器号
        machine_num = i_combo.get().replace(" ", "").replace("号机", "")

        # 根据机器号获取对应的IP地址
        value_dict['ip'] = iprex.get(machine_num, "127.0.0.1")

        value_dict['port'] = p_combo.get()
        value_dict['db'] = db_combo.get()
        value_dict['pwd'] = pwd_combo.get()

        # 立即触发更新值,而不是等待事件
        value_dict.update({
                'ip': value_dict['ip'],
                'port': value_dict['port'],
                'db': value_dict['db'],
                'pwd': value_dict['pwd']
        })


for i in range(4):
        value = dict()
        label = "label" + str(i)
        i_combo = "combo" + str(i * 3 + 1)
        p_combo = "combo" + str(i * 3 + 2)
        pwd_combo = "combo" + str(i * 3 + 4)
        db_combo = "combo" + str(i * 3 + 3)

        # 第一个下拉框
        label = tk.Label(root, text="主机%d:" % i)
        label.pack(pady=10)

        # 创建一个框架来容纳两个下拉框
        frame = tk.Frame(root)
        frame.pack(pady=5)

        # 调整下拉框间距
        label.pack(pady=5)  # 减小标签的垂直间距
        frame.pack(pady=2)  # 减小框架的垂直间距

        i_combo = ttk.Combobox(frame, values=options)
        i_combo.set(options[i])  # 设置默认值为第一个选项
        p_combo = ttk.Combobox(frame, values=options1)
        p_combo.set(options1[3])  # 设置默认值为第一个选项
        db_combo = ttk.Combobox(frame, values=options2)
        db_combo.set(options2[i])  # 设置默认值为第一个选项
        pwd_combo = ttk.Entry(frame, show="*")
        pwd_combo.insert(0, "qwe!@#SDF345788")  # Set default password
        i_combo.pack(side=tk.LEFT, padx=5)
        p_combo.pack(side=tk.LEFT, padx=5)
        db_combo.pack(side=tk.LEFT, padx=5)
        pwd_combo.pack(side=tk.LEFT, padx=5)

        # 创建一个字典来存储这组下拉框的值
        value = {'ip': '', 'port': '', 'db': '', "pwd": ""}
        ip_list.append(value)

        # 初始化默认值
        update_values(i_combo, p_combo, db_combo, pwd_combo, value)

        # 为每个下拉框添加回调函数
        i_combo.bind('<<ComboboxSelected>>',
                     lambda e, ic=i_combo, pc=p_combo, dbc=db_combo, pwd=pwd_combo, v=value: update_values(ic, pc, dbc,
                                                                                                           pwd, v))
        p_combo.bind('<<ComboboxSelected>>',
                     lambda e, ic=i_combo, pc=p_combo, dbc=db_combo, pwd=pwd_combo, v=value: update_values(ic, pc, dbc,
                                                                                                           pwd, v))
        db_combo.bind('<<ComboboxSelected>>',
                      lambda e, ic=i_combo, pc=p_combo, dbc=db_combo, pwd=pwd_combo, v=value: update_values(ic, pc, dbc,
                                                                                                            pwd, v))
        pwd_combo.bind('<KeyRelease>',
                       lambda e, ic=i_combo, pc=p_combo, dbc=db_combo, pwd=pwd_combo, v=value: update_values(ic, pc,
                                                                                                             dbc, pwd,
                                                                                                             v))

# 创建打印按钮的函数
def print_selections():
        # 创建结果窗口
        result_window = tk.Toplevel(root)
        result_window.title("Redis连接信息")
        result_window.geometry("400x400")

        # 创建日志输出框
        if not hasattr(result_window, 'log_text'):  # 如果还没有创建日志框
                log_frame = tk.Frame(result_window, bg='black', width=400, height=200)
                log_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
                log_frame.pack_propagate(False)  # 防止框架被内容压缩

                # 创建文本框用于显示日志
                log_text = tk.Text(log_frame, bg='black', fg='#00FF00',
                                   font=('Courier', 10), wrap=tk.WORD)
                log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                # 添加滚动条
                scrollbar = tk.Scrollbar(log_frame, command=log_text.yview)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                log_text.config(yscrollcommand=scrollbar.set)

                # 将日志文本框设为全局变量以便后续使用
                result_window.log_text = log_text

        # 显示选择结果
        result_window.log_text.delete(1.0, tk.END)  # 清空之前的日志
        for i, value in enumerate(ip_list):
                # result_text = f"主机{i}: IP={value['ip']}, Port={value['port']}, DB={value['db']},pwd={value['pwd']}\n"
                result_text = f"添加 主机{i}: IP={value['ip']} 成功！！\n"
                result_window.log_text.insert(tk.END, result_text)

        # 尝试连接Redis并显示结果
        for ip in ip_list:
                if ip["ip"] and ip["port"] and ip["db"] and ip["pwd"]:
                        try:
                                conn = Redis(ip["ip"], ip["port"], ip["db"], ip["pwd"])
                                # 获取所有键
                                keys = conn.keys()
                                result_window.log_text.insert(tk.END, f"Keys in database: {keys}\n")
                                # 获取数据库大小
                                dbsize = conn.dbsize()
                                result_window.log_text.insert(tk.END, f"Database size: {dbsize}\n")
                                # 获取服务器信息
                                info = conn.info()
                                result_window.log_text.insert(tk.END, f"Redis version: {info['redis_version']}\n")
                                result_window.log_text.insert(tk.END,
                                                              f"Connected clients: {info['connected_clients']}\n")
                                result_window.log_text.insert(tk.END, f"成功连接到 Redis: {conn}\n")
                        except Exception as e:
                                result_window.log_text.insert(tk.END, f"连接失败: {str(e)}\n")
                else:
                        result_window.log_text.insert(tk.END, "信息为空！！\n")


# 添加打印按钮
print_button = tk.Button(root, text="打印选择结果", command=print_selections)
print_button.pack(pady=20)

# 运行主循环
root.mainloop()




if __name__ == "__main__":
    run_code = 0
    pass
