import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import redis
from pymongo import MongoClient, WriteConcern
import threading
import time
from functools import partial
import concurrent.futures

class DatabaseMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Redis & MongoDB 监控工具")
        self.root.geometry("1200x800")
        
        # 创建Redis和MongoDB连接变量
        self.redis_clients = {}  # 存储多个redis连接
        self.mongo_conn = None   # 第一个MongoDB连接
        self.mongo_conn1 = None  # 第二个MongoDB连接
        
        # 创建自动刷新变量和监控状态
        self.auto_refresh = False
        self.refresh_thread = None
        self.monitoring = False
        
        # 地区信息字典
        self.area = {
        "heilongjiang":["181",15778,0,"fer@nhaweif576KUG","heilongjiang"],
        "xianggang":["181",10281,0,"*s,8<[VVS6h.nnWZ=cv{","xianggang"],
        "xinjiang":["191",18995,0,"fer@nhaweif576KUG","xinjiang"],
        "ningxia":["175",15456,0,"fer@nhaweif576KUG","ningxia"],
        "xizang":["175",18112,0,"fer@nhaweif576KUG","xizang"],
        "guangxi":["172",7933,0,"#Tn=EP(q%{","guangxi"],
        "neimenggu":["176",15347,0,"fer@nhaweif576KUG","neimenggu"],
        "taiwan":["167",10824,0,"e8Mzr}$%jsuCxKn4r#mm","taiwan"],
        "qinghai":["167",10824,0,"e8Mzr}$%jsuCxKn4r#mm","qinghai"],
        "gansu":["181",10281,0,"*s,8<[VVS6h.nnWZ=cv{","gansu"],
        "sanxi":["175",15768,0,"fer@nhaweif576KUG","sanxi"],
        "yunnan":["191",19113,0,"fer@nhaweif576KUG","yunnan"],
        "guizhou":["180",14307,0,"fer@nhaweif576KUG","guizhou"],
        "sichuan":["175",17112,0,"fer@nhaweif576KUG","sichuan"],
        "chongqing":["191",14117,0,"fer@nhaweif576KUG","chongqing"],
        "hainan":["181",14447,0,"fer@nhaweif576KUG","hainan"],
        "guangdong":["181",8499,0,"#Tn=EP(q%{","guangdong"],
        "hunan":["172",14771,0,"fer@nhaweif576KUG","hunan"],
        "hubei":["172",8723,0,"#Tn=EP(q%{","hubei"],
        "henan":["181",8679,0,"#Tn=EP(q%{","henan"],
        "shandong":["176",8490,0,"#Tn=EP(q%{","shandong"],
        "jiangxi":["172",15123,0,"fer@nhaweif576KUG","jiangxi"],
        "fujian":["167",14228,0,"uf$vU_1~wA0mB@Z+","fujian"],
        "anhui":["180",14117,0,"fer@nhaweif576KUG","anhui"],
        "zhejiang":["113",8490,0,"#Tn=EP(q%{","zhejiang"],
        "jiangsu":["172",14117,0,"fer@nhaweif576KUG","jiangsu"],
        "shanghai":["175",8490,0,"#Tn=EP(q%{","shanghai"],
        "jilin":["172",14991,0,"fer@nhaweif576KUG","jilin"],
        "liaoning":["176",15237,0,"fer@nhaweif576KUG","liaoning"],
        "shanxi":["176",16378,0,"fer@nhaweif576KUG","shanxi"],
        "hebei":["181",8577,0,"#Tn=EP(q%{","hebei"],
        "tianjin":["175",17659,0,"fer@nhaweif576KUG","tianjin"],
        "beijing":["180",8490,0,"redis2020redis","beijing"]
}
        
        # 地区键名映射
        self.key_map = {
            "taiwan": "A12",
            "xianggang": "VQ",
            "anhui": "IE",
            "qinghai": "VQ",
            "gansu": "VQ",
            "guangxi": "F6",
            "shandong": "E5",
            "zhejiang": "AV",
            "beijing": "SM",
            "guangdong": "40",
            "hebei": "NK",
            "shanghai": "KP",
            "jiangsu": "AN",
            "hubei": "OP",
            "fujian": "RA",
            "henan": "EH",
            "sichuan": "0T",
            "chongqing": "9E",
            "shanxi": "AB",
            "hainan": "MU",
            "tianjin": "G9",
            "heilongjiang": "PS",
            "jiangxi": "VM",
            "yunnan": "13C",
            "hunan": "RH",
            "jilin": "VR",
            "sanxi": "BA",
            "guizhou": "RT",
            "xizang": "5H0",
            "ningxia": "VD",
            "xinjiang": "8M",
            "neimenggu": "ML",
            "liaoning": "GK"
        }
        
        self.create_widgets()
    
    def create_widgets(self):
        # 创建顶部连接设置框架
        conn_frame = ttk.LabelFrame(self.root, text="连接设置")
        conn_frame.pack(fill="x", padx=10, pady=5)
        
        # 批量Redis连接设置
        redis_frame = ttk.LabelFrame(conn_frame, text="Redis 批量连接")
        redis_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        ttk.Label(redis_frame, text="Redis基础IP:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.redis_base_ip = ttk.Entry(redis_frame, width=15)
        self.redis_base_ip.insert(0, "192.168.5.")
        self.redis_base_ip.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(redis_frame, text="连接超时(秒):").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.redis_timeout = ttk.Spinbox(redis_frame, from_=1, to=10, width=5)
        self.redis_timeout.set(3)  # 默认3秒超时
        self.redis_timeout.grid(row=0, column=3, padx=5, pady=2)
        
        self.connect_all_redis_btn = ttk.Button(redis_frame, text="连接所有Redis", command=self.connect_all_redis)
        self.connect_all_redis_btn.grid(row=0, column=4, padx=5, pady=2)
        
        # MongoDB连接设置
        mongo_frame = ttk.LabelFrame(conn_frame, text="MongoDB 连接")
        mongo_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        ttk.Label(mongo_frame, text="主MongoDB (conn):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.mongo_host1 = ttk.Entry(mongo_frame, width=15)
        self.mongo_host1.insert(0, "192.168.5.167")
        self.mongo_host1.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(mongo_frame, text="端口:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.mongo_port1 = ttk.Entry(mongo_frame, width=6)
        self.mongo_port1.insert(0, "27017")
        self.mongo_port1.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(mongo_frame, text="中转MongoDB (conn1):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.mongo_host2 = ttk.Entry(mongo_frame, width=15)
        self.mongo_host2.insert(0, "192.168.5.113")
        self.mongo_host2.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(mongo_frame, text="端口:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.mongo_port2 = ttk.Entry(mongo_frame, width=6)
        self.mongo_port2.insert(0, "27017")
        self.mongo_port2.grid(row=1, column=3, padx=5, pady=2)
        
        self.connect_mongo_btn = ttk.Button(mongo_frame, text="连接MongoDB", command=self.connect_both_mongodb)
        self.connect_mongo_btn.grid(row=1, column=4, padx=5, pady=2)
        
        # 创建监控控制按钮
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_btn = ttk.Button(control_frame, text="开始监控", command=self.start_monitoring)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="停止监控", command=self.stop_monitoring, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        self.refresh_btn = ttk.Button(control_frame, text="手动刷新", command=self.refresh_data)
        self.refresh_btn.pack(side="left", padx=5)
        
        ttk.Label(control_frame, text="刷新间隔(秒):").pack(side="left", padx=5)
        self.refresh_interval = ttk.Spinbox(control_frame, from_=1, to=60, width=5)
        self.refresh_interval.set(5)
        self.refresh_interval.pack(side="left", padx=5)
        
        # 创建状态栏
        self.status_bar = ttk.Label(self.root, text="就绪", relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")
        
        # 创建选项卡
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=5)
        
        # Redis选项卡
        self.redis_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.redis_tab, text="Redis 监控")
        
        # MongoDB选项卡
        self.mongo_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.mongo_tab, text="MongoDB 监控")
        
        # 数据同步状态选项卡
        self.sync_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.sync_tab, text="数据同步状态")
        
        # 数据复制选项卡
        self.copy_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.copy_tab, text="数据复制")
        
        # 日志选项卡
        self.log_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.log_tab, text="日志")
        
        self.log_text = scrolledtext.ScrolledText(self.log_tab, wrap=tk.WORD)
        self.log_text.pack(expand=1, fill="both", padx=5, pady=5)
        
        # 设置Redis选项卡内容
        self.setup_redis_tab()
        
        # 设置MongoDB选项卡内容
        self.setup_mongo_tab()
        
        # 设置同步状态选项卡内容
        self.setup_sync_tab()
        
        # 设置数据复制选项卡内容
        self.setup_copy_tab()
        
        # 添加初始日志
        self.log("应用程序已启动，请配置连接设置")
    
    def setup_redis_tab(self):
        frame = ttk.Frame(self.redis_tab)
        frame.pack(expand=1, fill="both", padx=5, pady=5)
        
        # Redis信息显示
        info_frame = ttk.LabelFrame(frame, text="Redis上传数据计数(upkey:XX)")
        info_frame.pack(fill="both", expand=1, padx=5, pady=5)
        
        # 创建树状视图
        columns = ("region", "key", "upkey", "value", "mongo_count", "diff", "status")
        self.redis_upload_tree = ttk.Treeview(info_frame, columns=columns, show="headings")
        
        self.redis_upload_tree.heading("region", text="地区")
        self.redis_upload_tree.heading("key", text="键名前缀")
        self.redis_upload_tree.heading("upkey", text="完整键名")
        self.redis_upload_tree.heading("value", text="Redis上传数量")
        self.redis_upload_tree.heading("mongo_count", text="MongoDB实际数量")
        self.redis_upload_tree.heading("diff", text="未上传数量")
        self.redis_upload_tree.heading("status", text="连接状态")
        
        self.redis_upload_tree.column("region", width=80)
        self.redis_upload_tree.column("key", width=80)
        self.redis_upload_tree.column("upkey", width=120)
        self.redis_upload_tree.column("value", width=100)
        self.redis_upload_tree.column("mongo_count", width=120)
        self.redis_upload_tree.column("diff", width=100)
        self.redis_upload_tree.column("status", width=80)
        
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.redis_upload_tree.yview)
        self.redis_upload_tree.configure(yscrollcommand=scrollbar.set)
        
        self.redis_upload_tree.pack(side="left", fill="both", expand=1)
        scrollbar.pack(side="right", fill="y")
    
    def setup_mongo_tab(self):
        frame = ttk.Frame(self.mongo_tab)
        frame.pack(expand=1, fill="both", padx=5, pady=5)
        
        # MongoDB信息显示
        info_frame = ttk.LabelFrame(frame, text="MongoDB数据库信息")
        info_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(info_frame, text="主MongoDB状态:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.mongo1_status = ttk.Label(info_frame, text="未连接")
        self.mongo1_status.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(info_frame, text="中转MongoDB状态:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.mongo2_status = ttk.Label(info_frame, text="未连接")
        self.mongo2_status.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        
        # MongoDB集合数量对比
        db_frame = ttk.LabelFrame(frame, text="MongoDB集合数据对比")
        db_frame.pack(fill="both", expand=1, padx=5, pady=5)
        
        columns = ("region", "conn_docs", "conn1_docs", "diff", "sync_status")
        self.mongo_compare_tree = ttk.Treeview(db_frame, columns=columns, show="headings")
        
        self.mongo_compare_tree.heading("region", text="地区")
        self.mongo_compare_tree.heading("conn_docs", text="主MongoDB文档数")
        self.mongo_compare_tree.heading("conn1_docs", text="中转MongoDB文档数")
        self.mongo_compare_tree.heading("diff", text="未同步文档数")
        self.mongo_compare_tree.heading("sync_status", text="同步状态")
        
        self.mongo_compare_tree.column("region", width=100)
        self.mongo_compare_tree.column("conn_docs", width=120)
        self.mongo_compare_tree.column("conn1_docs", width=120)
        self.mongo_compare_tree.column("diff", width=100)
        self.mongo_compare_tree.column("sync_status", width=120)
        
        scrollbar = ttk.Scrollbar(db_frame, orient="vertical", command=self.mongo_compare_tree.yview)
        self.mongo_compare_tree.configure(yscrollcommand=scrollbar.set)
        
        self.mongo_compare_tree.pack(side="left", fill="both", expand=1)
        scrollbar.pack(side="right", fill="y")
    
    def setup_sync_tab(self):
        frame = ttk.Frame(self.sync_tab)
        frame.pack(expand=1, fill="both", padx=5, pady=5)
        
        # 同步状态总览
        info_frame = ttk.LabelFrame(frame, text="数据同步状态总览")
        info_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(info_frame, text="总文档数(主MongoDB):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.total_conn_docs = ttk.Label(info_frame, text="-")
        self.total_conn_docs.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        ttk.Label(info_frame, text="总文档数(中转MongoDB):").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.total_conn1_docs = ttk.Label(info_frame, text="-")
        self.total_conn1_docs.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        
        ttk.Label(info_frame, text="总未同步文档数:").grid(row=0, column=4, padx=5, pady=2, sticky="w")
        self.total_unsync_docs = ttk.Label(info_frame, text="-")
        self.total_unsync_docs.grid(row=0, column=5, padx=5, pady=2, sticky="w")
        
        ttk.Label(info_frame, text="同步完成率:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.sync_rate = ttk.Label(info_frame, text="-")
        self.sync_rate.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # 同步进度条
        ttk.Label(info_frame, text="同步进度:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.sync_progress = ttk.Progressbar(info_frame, orient="horizontal", length=200, mode="determinate")
        self.sync_progress.grid(row=1, column=3, padx=5, pady=2, columnspan=3, sticky="w")
        
        # 详细同步状态表格
        sync_frame = ttk.LabelFrame(frame, text="各地区同步详情")
        sync_frame.pack(fill="both", expand=1, padx=5, pady=5)
        
        columns = ("region", "redis_upkey", "redis_count", "conn_count", "conn1_count", "sync_status")
        self.sync_tree = ttk.Treeview(sync_frame, columns=columns, show="headings")
        
        self.sync_tree.heading("region", text="地区")
        self.sync_tree.heading("redis_upkey", text="Redis上传键")
        self.sync_tree.heading("redis_count", text="Redis记录上传数")
        self.sync_tree.heading("conn_count", text="主MongoDB文档数")
        self.sync_tree.heading("conn1_count", text="中转MongoDB文档数")
        self.sync_tree.heading("sync_status", text="同步状态")
        
        self.sync_tree.column("region", width=100)
        self.sync_tree.column("redis_upkey", width=120)
        self.sync_tree.column("redis_count", width=120)
        self.sync_tree.column("conn_count", width=120)
        self.sync_tree.column("conn1_count", width=120)
        self.sync_tree.column("sync_status", width=120)
        
        scrollbar = ttk.Scrollbar(sync_frame, orient="vertical", command=self.sync_tree.yview)
        self.sync_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sync_tree.pack(side="left", fill="both", expand=1)
        scrollbar.pack(side="right", fill="y")
    
    def setup_copy_tab(self):
        frame = ttk.Frame(self.copy_tab)
        frame.pack(expand=1, fill="both", padx=5, pady=5)
        
        # 复制控制区域
        control_frame = ttk.LabelFrame(frame, text="数据复制控制")
        control_frame.pack(fill="x", padx=5, pady=5)
        
        # 复制模式选择
        ttk.Label(control_frame, text="复制模式:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.copy_mode = tk.StringVar(value="selected")
        ttk.Radiobutton(control_frame, text="仅复制选中地区", variable=self.copy_mode, value="selected").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(control_frame, text="复制所有未完成地区", variable=self.copy_mode, value="incomplete").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(control_frame, text="复制所有地区", variable=self.copy_mode, value="all").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # 线程数设置
        ttk.Label(control_frame, text="并行线程数:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.thread_count = ttk.Spinbox(control_frame, from_=1, to=10, width=5)
        self.thread_count.set(6)  # 默认6个线程
        self.thread_count.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # 批处理大小设置
        ttk.Label(control_frame, text="批处理大小:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.batch_size = ttk.Spinbox(control_frame, from_=100, to=10000, width=7)
        self.batch_size.set(1000)  # 默认1000条记录一批
        self.batch_size.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        
        # 操作按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5)
        
        self.start_copy_btn = ttk.Button(button_frame, text="开始复制", command=self.start_data_copy)
        self.start_copy_btn.pack(side="left", padx=5)
        
        self.stop_copy_btn = ttk.Button(button_frame, text="停止复制", command=self.stop_data_copy, state="disabled")
        self.stop_copy_btn.pack(side="left", padx=5)
        
        # 复制进度区域
        progress_frame = ttk.LabelFrame(frame, text="复制进度")
        progress_frame.pack(fill="x", padx=5, pady=5)
        
        # 总体进度
        ttk.Label(progress_frame, text="总体进度:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.overall_progress = ttk.Progressbar(progress_frame, orient="horizontal", length=400, mode="determinate")
        self.overall_progress.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.overall_progress_label = ttk.Label(progress_frame, text="0/0")
        self.overall_progress_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        
        # 当前任务进度
        ttk.Label(progress_frame, text="当前任务:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.current_task_var = tk.StringVar(value="无任务")
        ttk.Label(progress_frame, textvariable=self.current_task_var).grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # 地区选择和状态显示
        regions_frame = ttk.LabelFrame(frame, text="地区复制状态")
        regions_frame.pack(fill="both", expand=1, padx=5, pady=5)
        
        # 创建树状视图
        columns = ("region", "source_count", "target_count", "remaining", "status", "progress")
        self.copy_tree = ttk.Treeview(regions_frame, columns=columns, show="headings", selectmode="extended")
        
        self.copy_tree.heading("region", text="地区")
        self.copy_tree.heading("source_count", text="源数据库文档数")
        self.copy_tree.heading("target_count", text="目标数据库文档数")
        self.copy_tree.heading("remaining", text="剩余文档数")
        self.copy_tree.heading("status", text="状态")
        self.copy_tree.heading("progress", text="进度")
        
        self.copy_tree.column("region", width=100)
        self.copy_tree.column("source_count", width=120)
        self.copy_tree.column("target_count", width=120)
        self.copy_tree.column("remaining", width=100)
        self.copy_tree.column("status", width=100)
        self.copy_tree.column("progress", width=100)
        
        scrollbar = ttk.Scrollbar(regions_frame, orient="vertical", command=self.copy_tree.yview)
        self.copy_tree.configure(yscrollcommand=scrollbar.set)
        
        self.copy_tree.pack(side="left", fill="both", expand=1)
        scrollbar.pack(side="right", fill="y")
        
        # 初始化复制状态变量
        self.copying = False
        self.copy_thread = None
        self.copy_tasks = []
        self.completed_tasks = 0
    
    def connect_all_redis(self):
        """连接所有地区的Redis服务器"""
        # 禁用连接按钮，避免重复点击
        self.connect_all_redis_btn.config(state="disabled")
        
        # 创建进度窗口
        self.progress_window = tk.Toplevel(self.root)
        self.progress_window.title("Redis连接进度")
        self.progress_window.geometry("400x200")
        self.progress_window.transient(self.root)
        self.progress_window.grab_set()
        self.progress_window.resizable(False, False)
        self.progress_window.protocol("WM_DELETE_WINDOW", self.cancel_redis_connect)
        
        # 添加进度信息
        ttk.Label(self.progress_window, text="正在连接Redis服务器...").pack(pady=10)
        
        # 添加当前地区标签
        self.current_region_var = tk.StringVar(value="准备连接...")
        ttk.Label(self.progress_window, textvariable=self.current_region_var).pack(pady=5)
        
        # 添加进度条
        total_regions = len(self.area)
        self.connect_progress = ttk.Progressbar(
            self.progress_window, orient="horizontal", length=350, 
            mode="determinate", maximum=total_regions
        )
        self.connect_progress.pack(pady=10)
        
        # 添加取消按钮
        ttk.Button(self.progress_window, text="取消", command=self.cancel_redis_connect).pack(pady=10)
        
        # 重置取消标志
        self.cancel_connect = False
        
        # 启动连接线程
        self.connect_thread = threading.Thread(target=self.connect_redis_thread, daemon=True)
        self.connect_thread.start()
    
    def connect_redis_instance(self, region_info):
        """连接单个Redis实例"""
        region = region_info[4]  # 地区名称
        ip_suffix = region_info[0]
        port = region_info[1]
        db = region_info[2]
        password = region_info[3]
        
        base_ip = self.redis_base_ip.get()
        host = f"{base_ip}{ip_suffix}"
        
        try:
            # 获取用户设置的超时时间
            timeout = int(self.redis_timeout.get())
            
            # 创建Redis客户端，确保设置严格的超时
            client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
                socket_timeout=timeout,
                socket_connect_timeout=timeout,
                health_check_interval=timeout
            )
            
            # 使用带超时的ping测试连接
            client.ping()
            
            # 返回成功结果
            return (region, client, True, "")
            
        except Exception as e:
            # 返回失败结果
            return (region, None, False, str(e))
    
    def connect_redis_thread(self):
        """后台线程连接所有Redis服务器"""
        base_ip = self.redis_base_ip.get()
        success_count = 0
        fail_count = 0
        total = len(self.area)
        
        # 使用更小的线程池，减少并发连接数
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            # 提交所有连接任务
            for region, region_info in self.area.items():
                # 更新当前正在连接的地区
                self.root.after(0, lambda r=region: self.current_region_var.set(f"正在连接: {r}"))
                
                # 提交连接任务
                future = executor.submit(self.connect_redis_instance, region_info)
                futures.append(future)
                
                # 增加延迟，避免同时发起太多连接
                time.sleep(0.2)
            
            # 处理连接结果
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if self.cancel_connect:
                    break
                
                result = future.result()
                region, client, success, error = result
                
                # 更新进度条
                self.root.after(0, lambda: self.connect_progress.step())
                
                if success:
                    # 存储成功连接的客户端
                    self.redis_clients[region] = client
                    success_count += 1
                    self.log(f"Redis连接成功: {region}")
                else:
                    fail_count += 1
                    self.log(f"Redis连接失败: {region} - {error}")
                
                # 更新进度信息
                progress_text = f"已完成: {i+1}/{total} (成功: {success_count}, 失败: {fail_count})"
                self.root.after(0, lambda t=progress_text: self.current_region_var.set(t))
        
        # 连接完成
        if self.cancel_connect:
            self.log("Redis连接过程已取消")
            final_message = "连接已取消"
        else:
            self.log(f"Redis批量连接完成: 成功 {success_count}，失败 {fail_count}")
            final_message = f"连接完成: 成功 {success_count}，失败 {fail_count}"
            
            # 刷新Redis数据
            self.root.after(0, self.refresh_redis_data)
        
        # 更新UI
        self.root.after(0, lambda: self.current_region_var.set(final_message))
        self.root.after(0, lambda: self.connect_all_redis_btn.config(state="normal"))
        
        # 短暂延迟后关闭进度窗口
        self.root.after(2000, self.close_progress_window)
    
    def cancel_redis_connect(self):
        """取消Redis连接过程"""
        self.cancel_connect = True
        self.close_progress_window()
    
    def close_progress_window(self):
        """关闭进度窗口"""
        if hasattr(self, 'progress_window') and self.progress_window.winfo_exists():
            self.progress_window.grab_release()
            self.progress_window.destroy()
            self.connect_all_redis_btn.config(state="normal")
    
    def connect_both_mongodb(self):
        """连接两个MongoDB服务器"""
        # 禁用连接按钮，避免重复点击
        self.connect_mongo_btn.config(state="disabled")
        
        # 创建进度窗口
        progress_window = tk.Toplevel(self.root)
        progress_window.title("MongoDB连接进度")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        progress_window.resizable(False, False)
        
        # 添加进度信息
        ttk.Label(progress_window, text="正在连接MongoDB服务器...").pack(pady=10)
        
        # 添加进度条
        progress = ttk.Progressbar(progress_window, orient="horizontal", length=350, mode="indeterminate")
        progress.pack(pady=10)
        progress.start(10)
        
        # 添加状态标签
        status_var = tk.StringVar(value="正在连接主MongoDB...")
        ttk.Label(progress_window, textvariable=status_var).pack(pady=5)
        
        # 添加取消按钮
        cancel_btn = ttk.Button(progress_window, text="取消", command=progress_window.destroy)
        cancel_btn.pack(pady=10)
        
        def connect_task():
            success = False
            error_msg = ""
            
            try:
                # 连接主MongoDB (conn)
                host1 = self.mongo_host1.get()
                port1 = int(self.mongo_port1.get())
                uri1 = f"mongodb://{host1}:{port1}/"
                
                # 更新状态
                self.root.after(0, lambda: status_var.set(f"正在连接主MongoDB: {uri1}"))
                
                # 使用超时设置
                mongo_conn = MongoClient(uri1, serverSelectionTimeoutMS=5000)
                
                # 测试连接
                mongo_conn.server_info()
                
                # 更新状态
                self.root.after(0, lambda: status_var.set(f"主MongoDB连接成功，正在连接中转MongoDB..."))
                
                # 连接中转MongoDB (conn1)
                host2 = self.mongo_host2.get()
                port2 = int(self.mongo_port2.get())
                uri2 = f"mongodb://{host2}:{port2}/"
                mongo_conn1 = MongoClient(uri2, serverSelectionTimeoutMS=5000)
                
                # 测试连接
                mongo_conn1.server_info()
                
                # 更新状态
                self.root.after(0, lambda: status_var.set("两个MongoDB服务器连接成功"))
                
                # 保存连接
                self.mongo_conn = mongo_conn
                self.mongo_conn1 = mongo_conn1
                
                success = True
                
            except Exception as e:
                error_msg = str(e)
                self.log(f"MongoDB连接失败: {error_msg}")
            
            # 在主线程中更新UI
            def update_ui():
                # 关闭进度窗口
                if progress_window.winfo_exists():
                    progress_window.destroy()
                
                if success:
                    # 更新状态
                    self.mongo1_status.config(text="已连接")
                    self.mongo2_status.config(text="已连接")
                    self.log(f"MongoDB连接成功")
                    
                    # 更新连接按钮
                    self.connect_mongo_btn.config(text="断开MongoDB", command=self.disconnect_both_mongodb, state="normal")
                    
                    # 刷新MongoDB数据
                    self.refresh_mongo_data()
                    
                    # 刷新复制状态
                    self.refresh_copy_status()
                else:
                    messagebox.showerror("连接错误", f"无法连接到MongoDB: {error_msg}")
                    self.connect_mongo_btn.config(state="normal")
            
            self.root.after(0, update_ui)
        
        # 启动连接线程
        threading.Thread(target=connect_task, daemon=True).start()
    
    def disconnect_both_mongodb(self):
        """断开两个MongoDB连接"""
        if self.mongo_conn:
            self.mongo_conn.close()
            self.mongo_conn = None
            self.mongo1_status.config(text="未连接")
        
        if self.mongo_conn1:
            self.mongo_conn1.close()
            self.mongo_conn1 = None
            self.mongo2_status.config(text="未连接")
        
        # 清空数据
        self.mongo_compare_tree.delete(*self.mongo_compare_tree.get_children())
        self.sync_tree.delete(*self.sync_tree.get_children())
        
        # 更新连接按钮
        self.connect_mongo_btn.config(text="连接MongoDB", command=self.connect_both_mongodb)
        
        self.log("MongoDB已断开连接")
    
    def refresh_redis_data(self):
        """刷新Redis数据"""
        if not self.redis_clients:
            return
        
        # 清空现有数据
        self.redis_upload_tree.delete(*self.redis_upload_tree.get_children())
        
        for region, client in self.redis_clients.items():
            try:
                # 获取该地区的键名前缀
                key_prefix = self.key_map.get(region, "")
                upkey = f"upkey:{key_prefix}"
                
                # 获取上传计数值并乘以100
                value = client.get(upkey)
                redis_count = "0"
                if value:
                    try:
                        # 尝试将值转换为整数并乘以100
                        redis_count = str(int(value) * 100)
                    except ValueError:
                        redis_count = value
                
                # 获取MongoDB中的实际文档数
                mongo_count = "-"
                diff_count = "-"
                
                if self.mongo_conn1:
                    try:
                        # 获取中转MongoDB中的文档数
                        mongo_count = self.mongo_conn1[region]["sorcomp"].estimated_document_count()
                        
                        # 计算差异
                        if redis_count != "-" and redis_count != "0":
                            redis_num = int(redis_count)
                            diff = max(0, redis_num - mongo_count)
                            diff_count = str(diff)
                    except Exception:
                        mongo_count = "-"
                
                # 添加到表格
                self.redis_upload_tree.insert("", "end", values=(
                    region, key_prefix, upkey, redis_count, mongo_count, diff_count, "已连接"
                ))
                
            except Exception as e:
                # 连接可能已断开
                self.redis_upload_tree.insert("", "end", values=(
                    region, self.key_map.get(region, ""), 
                    f"upkey:{self.key_map.get(region, '')}", 
                    "-", "-", "-", "连接失败"
                ))
                self.log(f"刷新Redis数据失败: {region} - {str(e)}")
        
        self.log("已刷新Redis上传计数数据")
    
    def refresh_mongo_data(self):
        """刷新MongoDB数据"""
        if not self.mongo_conn or not self.mongo_conn1:
            return
        
        # 清空现有数据
        self.mongo_compare_tree.delete(*self.mongo_compare_tree.get_children())
        self.sync_tree.delete(*self.sync_tree.get_children())
        
        total_conn_docs = 0
        total_conn1_docs = 0
        total_diff = 0
        
        for region in self.area.keys():
            try:
                # 获取主MongoDB中的文档数
                db_name = region
                coll_name = "sorcomp"
                conn_count = 0
                
                try:
                    conn_count = self.mongo_conn[db_name][coll_name].estimated_document_count()
                except Exception:
                    conn_count = 0
                
                # 获取中转MongoDB中的文档数
                conn1_count = 0
                try:
                    conn1_count = self.mongo_conn1[db_name][coll_name].estimated_document_count()
                except Exception:
                    conn1_count = 0
                
                # 计算差异
                diff = max(0, conn_count - conn1_count)
                
                # 确定同步状态
                if conn_count == 0:
                    sync_status = "无数据"
                elif diff == 0:
                    sync_status = "已完成"
                elif conn1_count > 0:
                    sync_status = f"进行中 ({int((conn1_count/conn_count)*100)}%)"
                else:
                    sync_status = "未开始"
                
                # 添加到表格
                self.mongo_compare_tree.insert("", "end", values=(
                    region, conn_count, conn1_count, diff, sync_status
                ))
                
                # 获取Redis上传计数
                redis_count = "-"
                redis_key = self.key_map.get(region, "")
                upkey = f"upkey:{redis_key}"
                
                if region in self.redis_clients:
                    try:
                        redis_value = self.redis_clients[region].get(upkey)
                        if redis_value:
                            try:
                                # 尝试将值转换为整数并乘以100（而不是1000）
                                redis_count = str(int(redis_value) * 100)
                            except ValueError:
                                redis_count = redis_value
                        else:
                            redis_count = "0"
                    except:
                        redis_count = "-"
                
                # 添加到同步详情表格
                self.sync_tree.insert("", "end", values=(
                    region, upkey, redis_count, conn_count, conn1_count, sync_status
                ))
                
                # 累计总数
                total_conn_docs += conn_count
                total_conn1_docs += conn1_count
                total_diff += diff
                
            except Exception as e:
                self.log(f"刷新MongoDB数据失败: {region} - {str(e)}")
        
        # 更新总览数据
        self.total_conn_docs.config(text=str(total_conn_docs))
        self.total_conn1_docs.config(text=str(total_conn1_docs))
        self.total_unsync_docs.config(text=str(total_diff))
        
        # 计算同步率和进度
        if total_conn_docs > 0:
            sync_rate = ((total_conn_docs - total_diff) / total_conn_docs) * 100
            self.sync_rate.config(text=f"{sync_rate:.2f}%")
            self.sync_progress["value"] = sync_rate
        else:
            self.sync_rate.config(text="0%")
            self.sync_progress["value"] = 0
        
        self.log("已刷新MongoDB数据对比")
    
    def refresh_data(self):
        """手动刷新所有数据"""
        self.refresh_redis_data()
        self.refresh_mongo_data()
        self.refresh_copy_status()
    
    def start_monitoring(self):
        """开始自动监控"""
        if self.monitoring:
            return
        
        try:
            interval = int(self.refresh_interval.get())
            if interval < 1:
                raise ValueError("刷新间隔必须大于0")
            
            self.monitoring = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            def monitor_task():
                while self.monitoring:
                    self.refresh_data()
                    for i in range(interval):
                        if not self.monitoring:
                            break
                        time.sleep(1)
            
            self.refresh_thread = threading.Thread(target=monitor_task)
            self.refresh_thread.daemon = True
            self.refresh_thread.start()
            
            self.log(f"已开始自动监控，刷新间隔: {interval}秒")
            self.status_bar.config(text=f"监控中 - 刷新间隔: {interval}秒")
            
        except Exception as e:
            self.log(f"启动监控失败: {str(e)}")
            messagebox.showerror("监控错误", f"无法启动监控: {str(e)}")
    
    def stop_monitoring(self):
        """停止自动监控"""
        self.monitoring = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log("已停止自动监控")
        self.status_bar.config(text="就绪")
    
    def log(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def start_data_copy(self):
        """开始数据复制"""
        if not self.mongo_conn or not self.mongo_conn1:
            messagebox.showerror("错误", "请先连接MongoDB服务器")
            return
        
        if self.copying:
            return
        
        # 获取复制模式
        mode = self.copy_mode.get()
        
        # 确定要复制的地区
        regions_to_copy = []
        
        if mode == "selected":
            # 获取选中的地区
            selected_items = self.copy_tree.selection()
            if not selected_items:
                messagebox.showinfo("提示", "请选择要复制的地区")
                return
            
            for item in selected_items:
                region = self.copy_tree.item(item, "values")[0]
                regions_to_copy.append(region)
        
        elif mode == "incomplete":
            # 获取所有未完成的地区
            for item in self.copy_tree.get_children():
                values = self.copy_tree.item(item, "values")
                region = values[0]
                status = values[4]
                if status != "已完成":
                    regions_to_copy.append(region)
        
        else:  # mode == "all"
            # 获取所有地区
            for item in self.copy_tree.get_children():
                region = self.copy_tree.item(item, "values")[0]
                regions_to_copy.append(region)
        
        if not regions_to_copy:
            messagebox.showinfo("提示", "没有需要复制的地区")
            return
        
        # 更新UI状态
        self.copying = True
        self.start_copy_btn.config(state="disabled")
        self.stop_copy_btn.config(state="normal")
        
        # 准备复制任务
        self.copy_tasks = regions_to_copy
        self.completed_tasks = 0
        
        # 更新进度条
        self.overall_progress["maximum"] = len(self.copy_tasks)
        self.overall_progress["value"] = 0
        self.overall_progress_label.config(text=f"0/{len(self.copy_tasks)}")
        
        # 启动复制线程
        self.copy_thread = threading.Thread(target=self.copy_data_thread, daemon=True)
        self.copy_thread.start()
        
        self.log(f"开始复制数据，共 {len(regions_to_copy)} 个地区")

    def stop_data_copy(self):
        """停止数据复制"""
        if not self.copying:
            return
        
        self.copying = False
        self.stop_copy_btn.config(state="disabled")
        self.current_task_var.set("正在停止...")
        
        # 等待线程结束
        if self.copy_thread and self.copy_thread.is_alive():
            self.copy_thread.join(0.1)
        
        self.start_copy_btn.config(state="normal")
        self.current_task_var.set("已停止")
        self.log("数据复制已停止")

    def copy_data_thread(self):
        """后台线程复制数据"""
        from pymongo import WriteConcern
        import concurrent.futures
        
        # 获取线程数和批处理大小
        thread_count = int(self.thread_count.get())
        batch_size = int(self.batch_size.get())
        
        # 使用线程池并行复制
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            # 提交所有复制任务
            for region in self.copy_tasks:
                # 更新当前任务
                self.root.after(0, lambda r=region: self.current_task_var.set(f"正在复制: {r}"))
                
                # 更新地区状态
                for item in self.copy_tree.get_children():
                    if self.copy_tree.item(item, "values")[0] == region:
                        self.root.after(0, lambda i=item: self.copy_tree.item(i, values=(
                            *self.copy_tree.item(i, "values")[:4], "复制中", "0%"
                        )))
                        break
                
                # 提交复制任务
                future = executor.submit(self.copy_collection_for_region, region, batch_size)
                futures.append((region, future))
            
            # 处理复制结果
            for region, future in futures:
                if not self.copying:
                    break
                
                try:
                    result = future.result()
                    success, source_count, target_count, error = result
                    
                    # 更新地区状态
                    for item in self.copy_tree.get_children():
                        if self.copy_tree.item(item, "values")[0] == region:
                            if success:
                                status = "已完成"
                                progress = "100%"
                            else:
                                status = f"失败: {error}"
                                progress = "0%"
                            
                            self.root.after(0, lambda i=item, s=source_count, t=target_count, st=status, p=progress: 
                                           self.copy_tree.item(i, values=(
                                               region, s, t, max(0, s-t), st, p
                                           )))
                            break
                    
                    # 更新进度
                    self.completed_tasks += 1
                    self.root.after(0, lambda: self.overall_progress.step())
                    self.root.after(0, lambda: self.overall_progress_label.config(
                        text=f"{self.completed_tasks}/{len(self.copy_tasks)}"
                    ))
                    
                    if success:
                        self.log(f"地区 {region} 复制完成，共 {source_count} 条记录")
                    else:
                        self.log(f"地区 {region} 复制失败: {error}")
                    
                except Exception as e:
                    self.log(f"复制 {region} 时出现错误: {str(e)}")
        
        # 复制完成
        if self.copying:
            self.root.after(0, lambda: self.current_task_var.set("复制完成"))
            self.root.after(0, self.refresh_mongo_data)  # 刷新MongoDB数据
            self.log("所有数据复制任务已完成")
        
        # 重置UI状态
        self.copying = False
        self.root.after(0, lambda: self.start_copy_btn.config(state="normal"))
        self.root.after(0, lambda: self.stop_copy_btn.config(state="disabled"))

    def copy_collection_for_region(self, region, batch_size):
        """复制单个地区的集合"""
        try:
            db_name = region
            collection_name = "sorcomp"
            
            # 获取源集合和目标集合
            source_db = self.mongo_conn[db_name]
            target_db = self.mongo_conn1[db_name]
            source_collection = source_db[collection_name]
            target_collection = target_db[collection_name]
            
            # 获取源集合文档数
            source_count = source_collection.estimated_document_count()
            
            # 如果源集合为空，直接返回
            if source_count == 0:
                return True, 0, 0, ""
            
            # 删除目标集合中的所有数据
            target_collection.delete_many({})
            
            # 复制索引（如果有的话）
            indexes = source_collection.index_information()
            for index_name, index_info in indexes.items():
                if index_name != '_id_':  # 跳过默认的 _id 索引
                    target_collection.create_index(index_info['key'])
            
            # 复制数据：批量插入
            current_page = 0
            last_id = None  # 用于存储上一批数据的最后一个文档的 _id
            total_copied = 0
            write_concern = WriteConcern(w=1)
            
            while self.copying:
                # 构建查询
                query = {}
                if last_id:
                    query["_id"] = {"$gt": last_id}  # 基于 _id 分页
                
                # 获取一批数据
                docs_cursor = source_collection.find(query).sort("_id", 1).limit(batch_size)
                docs = list(docs_cursor)
                
                if not docs:  # 如果没有数据，退出循环
                    break
                
                # 批量插入数据到目标集合
                target_collection.with_options(write_concern=write_concern).insert_many(docs)
                total_copied += len(docs)
                
                # 更新进度
                progress = min(100, int((total_copied / source_count) * 100))
                for item in self.copy_tree.get_children():
                    if self.copy_tree.item(item, "values")[0] == region:
                        self.root.after(0, lambda i=item, p=progress, t=total_copied: 
                                       self.copy_tree.item(i, values=(
                                           region, source_count, t, max(0, source_count-t), 
                                           "复制中", f"{p}%"
                                       )))
                        break
                
                # 更新 last_id 和页码
                last_id = docs[-1]["_id"]
                current_page += 1
                
                # 检查是否已停止
                if not self.copying:
                    break
            
            # 获取目标集合文档数
            target_count = target_collection.estimated_document_count()
            
            # 返回结果
            if self.copying:
                return True, source_count, target_count, ""
            else:
                return False, source_count, target_count, "用户取消"
            
        except Exception as e:
            return False, 0, 0, str(e)

    def refresh_copy_status(self):
        """刷新复制状态表格"""
        if not self.mongo_conn or not self.mongo_conn1:
            return
        
        # 清空现有数据
        self.copy_tree.delete(*self.copy_tree.get_children())
        
        for region in self.area.keys():
            try:
                # 获取主MongoDB中的文档数
                db_name = region
                coll_name = "sorcomp"
                source_count = 0
                
                try:
                    source_count = self.mongo_conn[db_name][coll_name].estimated_document_count()
                except Exception:
                    source_count = 0
                
                # 获取中转MongoDB中的文档数
                target_count = 0
                try:
                    target_count = self.mongo_conn1[db_name][coll_name].estimated_document_count()
                except Exception:
                    target_count = 0
                
                # 计算剩余文档数
                remaining = max(0, source_count - target_count)
                
                # 确定同步状态
                if source_count == 0:
                    status = "无数据"
                    progress = "0%"
                elif remaining == 0:
                    status = "已完成"
                    progress = "100%"
                elif target_count > 0:
                    status = "部分完成"
                    progress_value = int((target_count / source_count) * 100)
                    progress = f"{progress_value}%"
                else:
                    status = "未开始"
                    progress = "0%"
                
                # 添加到表格
                self.copy_tree.insert("", "end", values=(
                    region, source_count, target_count, remaining, status, progress
                ))
                
            except Exception as e:
                self.log(f"获取 {region} 复制状态失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseMonitor(root)
    root.mainloop() 