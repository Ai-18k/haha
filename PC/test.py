import pymongo
import time

def test_mongodb_connection():
    print("MongoDB连接测试开始...")
    
    # 测试参数
    hosts = [
        {"name": "主MongoDB (conn)", "host": "192.168.5.167", "port": 27017},
        {"name": "中转MongoDB (conn1)", "host": "192.168.5.113", "port": 27017}
    ]
    
    for db in hosts:
        print(f"\n测试连接 {db['name']}...")
        start_time = time.time()
        
        try:
            # 设置较短的超时时间
            uri = f"mongodb://{db['host']}:{db['port']}/"
            client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
            
            # 测试连接
            print(f"  尝试连接到 {uri}")
            server_info = client.server_info()
            
            # 获取版本信息
            version = server_info.get("version", "未知")
            print(f"  连接成功! MongoDB版本: {version}")
            
            # 尝试列出数据库
            print(f"  可用数据库列表:")
            dbs = client.list_database_names()
            for db_name in dbs:
                print(f"    - {db_name}")
                
                # 如果是我们关心的数据库，检查sorcomp集合
                if db_name not in ["admin", "local", "config"]:
                    try:
                        count = client[db_name]["sorcomp"].count_documents({})
                        print(f"      sorcomp集合文档数: {count}")
                    except Exception as e:
                        print(f"      无法获取sorcomp集合信息: {str(e)}")
            
            # 关闭连接
            client.close()
            
        except pymongo.errors.ServerSelectionTimeoutError:
            print(f"  错误: 连接超时。服务器可能未运行或网络问题。")
        except pymongo.errors.ConnectionFailure:
            print(f"  错误: 无法连接到服务器。")
        except Exception as e:
            print(f"  错误: {str(e)}")
        
        elapsed = time.time() - start_time
        print(f"  测试耗时: {elapsed:.2f}秒")
    
    print("\nMongoDB连接测试完成。")

if __name__ == "__main__":
    test_mongodb_connection()