import os
import sys
import subprocess

def run_pyinstaller():
    """运行PyInstaller打包程序"""
    print("开始打包 Redis & MongoDB 监控工具...")
    
    # 确保安装了PyInstaller
    try:
        import PyInstaller
        print(f"已检测到PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("未检测到PyInstaller，正在安装...")
        subprocess.call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 确保安装了所需依赖
    dependencies = ["redis", "pymongo"]
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"已检测到 {dep}")
        except ImportError:
            print(f"未检测到 {dep}，正在安装...")
            subprocess.call([sys.executable, "-m", "pip", "install", dep])
    
    # 打包命令
    cmd = [
        "pyinstaller",
        "--name=RedisMongoMonitor",
        "--onefile",                   # 生成单个EXE文件
        "--windowed",                  # Windows下不显示控制台
        "--icon=1.jpg",             # 图标(如果有)
        "--add-data=README.md;.",      # 添加说明文件(如果有)
        "--clean",                     # 清理临时文件
        "redis_mongodb_monitor.py"     # 主Python文件
    ]
    
    # 检查图标文件是否存在，不存在则移除相关参数
    if not os.path.exists("1.jpg"):
        cmd.remove("--icon=1.jpg")
        print("警告: 未找到图标文件，将使用默认图标")
    
    # 检查说明文件是否存在，不存在则移除相关参数
    if not os.path.exists("README.md"):
        cmd.remove("--add-data=README.md;.")
        print("警告: 未找到README.md文件")
    
    # 运行打包命令
    try:
        print("\n正在执行打包命令...\n")
        subprocess.call(cmd)
        print("\n打包完成!")
        print("\n可执行文件位于 dist/RedisMongoMonitor.exe")
    except Exception as e:
        print(f"打包过程中出现错误: {str(e)}")

if __name__ == "__main__":
    run_pyinstaller()
