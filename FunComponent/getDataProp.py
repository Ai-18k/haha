import json

from loguru import logger
from redis.client import Redis
from config import checkconfig, filtermap
from pymongo import MongoClient
# 获取工商各个数据占总数居占比信息

def filtermap(area):
    if area in ["jiangsu","guangxi","hunan","hubei","jiangxi","jilin"]:
        return "jsAddr"
    elif area in ["fujian","guizhou","anhui","beijing","qinghai"]:
        return "fjAddr"
    elif area in ["gansu","guangdong","hainan","hebei","heilongjiang","henan"]:
        return "gsAddr"
    elif area in ["chongqing","yunnan","xinjiang","zhejiang","taiwan"]:
        return "cqAddr"
    elif area in ["shanxi", "neimenggu", "liaoning","shandong","xianggang"]:
        return "sdAddr"
    elif area in ["xizang","tianjin","sichuan","shanghai","ningxia","sanxi"]:
        return "shAddr"
    else:
        return area

def checkconfig(area):
    filterAddr = filtermap(area)
    with open("config.json", "r", encoding="utf-8") as file:
        config = file.read()
    config = json.loads(config)
    serv_conn = Redis('139.9.70.%s' % config["serverAddr"][0],
                      config["serverAddr"][1],
                      config["serverAddr"][2],
                      config["serverAddr"][3],
                      socket_connect_timeout=config["serverAddr"][4])
    addr=serv_conn.get(area)
    config["servSAddr"]=json.loads(serv_conn.get("servSAddr").decode("utf-8"))
    try:
        config[filterAddr] = json.loads(serv_conn.get(filterAddr).decode("utf-8"))
    except:
        print("未知地址")
    config["localSAddr"]=json.loads(serv_conn.get("localSAddr").decode("utf-8"))
    addr = json.loads(addr.decode())
    config["fAddr"]=addr
    if 'localSAddr' not in config:
        logger.error("请设置数据保存地址！！")
        raise "未设置文件保存地址"
    else:
        if len(config['localSAddr'])<2:
            logger.error("请 正确配置 数据保存地址！！")
            raise "未正确配文件保存地址"
    if not serv_conn.exists(area):
        logger.error("未找到与之相关的设备信息，请检查名称或者检查设备是否存在")
        raise "名称有误或者设备不存在，请检查！！"
    config["uAddr"]=json.loads(serv_conn.get("bendi"))
    config["rkey"]=area
    config["area"]=area
    _isproxy=json.loads(serv_conn.get("proxy:_isUse").decode("utf-8"))
    if _isproxy["isUse"]:
        config["proxy"]=_isproxy["info"]
    else:
        config["proxy"]=False
    return config


area_list = [
            "anhui",
            "beijing",
            "chongqing",
            "fujian",
            "gansu",
            "guangdong",
            "guangxi",
            "guizhou",
            "hainan",
            "hebei",
            "heilongjiang",
            "henan",
            "hubei",
            "hunan",
            "jiangsu",
            "jiangxi",
            "jilin",
            "liaoning",
            "neimenggu",
            "ningxia",
            "qinghai",
            "sanxi",
            "shandong",
            "shanghai",
            "shanxi",
            "sichuan",
            "tianjin",
            "xinjiang",
            "xizang",
            "yunnan",
            "zhejiang"
]
allmap=[]
for area in area_list:
    config = checkconfig(area)
    filterAddr = filtermap(area)
    serv_client = MongoClient(host="192.168.5.%s" % config[filterAddr][0],
                              port=config[filterAddr][1],
                              username=config[filterAddr][2],
                              password=config[filterAddr][3],
                              authSource=config[filterAddr][4])
    print("*"*100)
    keys = ["rzzzq","sfaj","sbxx","dxxk","zzzs","zpzzq","h_cpws_com","cpws_com","zlxx_com","xzxk"]
    for key in keys:
        keymap={
            "rzzzq":"软著著作权",
            "sfaj":"司法",
            "sbxx":"商标信息",
            "dxxk":"电信许可",
            "zzzs":"资质证书",
            "zpzzq":"作品著作权",
            "h_cpws_com":"历史裁判文书",
            "cpws_com":"裁判文书",
            "zlxx_com":"专利信息",
            "xzxk":"行政许可"
        }
        db = serv_client[area]["filter_" + key]
        totalnum=serv_client[area]["filter_company_id"].estimated_document_count()
        if area=="hebei":
            totalnum =4354562
        if totalnum == 0:
            Percentage=0
        else:
            num=db.estimated_document_count()
            print(num,totalnum)
            Percentage=(num/totalnum)*100
            print(f"处理键: {key} 已完成 {Percentage}")
            allmap.append({"city":area,keymap[key]:f"已完成{num} 总{totalnum} {int(Percentage)}%"})
    print(f"【{area}】 :【{serv_client}】")

pmap= {
    "anhui": "安徽",
    "beijing": "北京",
    "chongqing": "重庆",
    "fujian": "福建",
    "gansu": "甘肃",
    "guangdong": "广东",
    "guangxi": "广西",
    "guizhou": "贵州",
    "hainan": "海南",
    "hebei": "河北",
    "heilongjiang": "黑龙江",
    "henan": "河南",
    "hubei": "湖北",
    "hunan": "湖南",
    "jiangsu": "江苏",
    "jiangxi": "江西",
    "jilin": "吉林",
    "liaoning": "辽宁",
    "neimenggu": "内蒙古",
    "ningxia": "宁夏",
    "qinghai": "青海",
    "sanxi": "陕西",
    "shandong": "山东",
    "shanghai": "上海",
    "shanxi": "山西",
    "sichuan": "四川",
    "tianjin": "天津",
    "xinjiang": "新疆",
    "xizang": "西藏",
    "yunnan": "云南",
    "zhejiang": "浙江"
}
for yy in allmap:
    if "软著著作权" in yy:
        with open(rf"C:\Users\Administrator\Desktop\%s.txt"%"软著著作权","a",encoding="utf-8") as f:
            f.write(pmap[yy["city"]]+":"+yy["软著著作权"]+"\n")
    if "司法" in yy:
        with open(rf"C:\Users\Administrator\Desktop\%s.txt"%"司法","a",encoding="utf-8") as f:
            f.write(pmap[yy["city"]]+":"+yy["司法"]+"\n")
    if "商标信息" in yy:
        with open(rf"C:\Users\Administrator\Desktop\%s.txt"%"商标信息","a",encoding="utf-8") as f:
            f.write(pmap[yy["city"]]+":"+yy["商标信息"]+"\n")
    if "电信许可" in yy:
        with open(rf"C:\Users\Administrator\Desktop\%s.txt"%"电信许可","a",encoding="utf-8") as f:
            f.write(pmap[yy["city"]] + ":" + yy["电信许可"] + "\n")
    if "资质证书" in yy:
        with open(rf"C:\Users\Administrator\Desktop\%s.txt"%"资质证书","a",encoding="utf-8") as f:
            f.write(pmap[yy["city"]]+":"+yy["资质证书"]+"\n")
    if "作品著作权" in yy:
        with open(rf"C:\Users\Administrator\Desktop\%s.txt"%"作品著作权","a",encoding="utf-8") as f:
            f.write(pmap[yy["city"]]+":"+yy["作品著作权"]+"\n")
    if "历史裁判文书" in yy:
        with open(rf"C:\Users\Administrator\Desktop\%s.txt"%"历史裁判文书","a",encoding="utf-8") as f:
            f.write(pmap[yy["city"]] + ":" + yy["历史裁判文书"] + "\n")
    if "专利信息" in yy:
        with open(rf"C:\Users\Administrator\Desktop\%s.txt"%"专利信息","a",encoding="utf-8") as f:
            f.write(pmap[yy["city"]]+":"+yy["专利信息"]+"\n")
    if "行政许可" in yy:
        with open(rf"C:\Users\Administrator\Desktop\%s.txt"%"行政许可","a",encoding="utf-8") as f:
            f.write(pmap[yy["city"]]+":"+yy["行政许可"]+"\n")
    if "裁判文书" in yy:
        with open(rf"C:\Users\Administrator\Desktop\%s.txt"%"裁判文书","a",encoding="utf-8") as f:
            f.write(pmap[yy["city"]]+":"+yy["裁判文书"]+"\n")



