import json

from redis.client import Redis
from config import checkconfig, filtermap

# 获取工商各个数据占总数居占比信息

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
    print("*"*100)
    local_conn = Redis("192.168.5.%s" % config["fAddr"][0],
                            config["fAddr"][1],
                            config["fAddr"][2],
                            config["fAddr"][3],
                            socket_connect_timeout=1170)
    pattern = area + ":filter*"
    keys = local_conn.keys(pattern)
    for key in keys:
        rr=key.decode().split(":")[-1]
        print(rr)
        if rr in ["rzzzq","sfaj","sbxx","dxxk","zzzs","zpzzq","h_cpws_com","cpws_com","zlxx_com","xzxk"]:
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
            coll=keymap[rr]
            totalnum=local_conn.scard(area+":filter:company_id")
            if area=="hebei":
                totalnum =4354562
            if totalnum == 0:
                Percentage=0
            else:
                num=local_conn.scard(key.decode())
                print(num,totalnum)
                Percentage=(num/totalnum)*100
            print(f"处理键: {key.decode()} 已完成 {Percentage}")
            allmap.append({"city":area,coll:f"已完成{num} 总{totalnum} {int(Percentage)}%"})
    print(f"【{area}】 :【{local_conn}】")
    print(f"找到 {len(keys)} 个匹配 '{pattern}' 的键")
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
    "sanxi": "陕西",  # 注意：拼音应为"shanxi"，但您提供的是"sanxi"
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



