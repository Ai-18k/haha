
from pymongo import MongoClient
from redis.client import Redis

area="fujian"

#数据库连接对象
serv_conn = Redis(host='182.43.38.79', port=6379, db=5, password="lzh990130",socket_connect_timeout=70)
new_serv_conn = Redis(host='139.9.70.234', port=6379, db=2, password="anbo123",socket_connect_timeout=70)
local_conn = Redis(host='192.168.5.167', port=9736, db=0, password="3r332r@",socket_connect_timeout=70)
local_T4_conn = Redis(host='192.168.5.87', port=7933, db=0, password="fer@nhaweif576KUG",socket_connect_timeout=70)


# mongo连接对象
client = MongoClient(host='192.168.5.167', port=27017)
serv_client = MongoClient(host='139.9.70.234', port=12700, username="root", password="QuyHlxXhW2PSHTwT",authSource="admin")

"""mongo需要的库"""
# 服务器Mongo数据配置
# company
coll=serv_client[area]["company_id"]
coll1=serv_client["company"][area]["company"]
#司法
coll2=serv_client[area]["司法案件"]
coll3=serv_client[area]["专利"]

# 法院公告  被执行人  经营异常   限制消费  裁判文书  失信被执行人 行政处罚  股权冻结
fygg=serv_client[area]["法院公告"]
bzxr=serv_client[area]["被执行人"]
jyyc=serv_client[area]["经营异常"]
xzxf=serv_client[area]["限制消费"]
cpws=serv_client[area]["裁判文书"]
sxzx=serv_client[area]["失信被执行人"]
xzcf=serv_client[area]["行政处罚"]
gqdj=serv_client[area]["股权冻结"]

# 历史数据-------->历史法院公告  历史经营异常  历史限制消费 历史裁判文书  历史被执行人 历史失信被执行人  历史行政处罚  历史股权冻结
h_fygg=serv_client[area]["历史法院公告"]
h_jyyc=serv_client[area]["历史经营异常"]
h_xzxf=serv_client[area]["历史限制消费"]
h_cpws=serv_client[area]["历史裁判文书"]
h_bzxr=serv_client[area]["历史被执行人"]
h_sxzx=serv_client[area]["历史失信被执行人"]
h_xzcf=serv_client[area]["历史行政处罚"]
h_gqdj=serv_client[area]["历史股权冻结"]

sb = serv_client[area]['商标信息']
zpzz = serv_client[area]['作品著作权']
dxxk = serv_client[area]['电信许可']
rzzq = serv_client[area]['软著著作权']
xzxk = serv_client[area]['行政许可']
zzzs = serv_client[area]['资质证书']


# 本地mongo数据保存
# 法院公告  被执行人  经营异常   限制消费  裁判文书  失信被执行人 行政处罚  股权冻结
l_fygg=serv_client[area]["法院公告"]
l_bzxr=serv_client[area]["被执行人"]
l_jyyc=serv_client[area]["经营异常"]
l_xzxf=serv_client[area]["限制消费"]
l_cpws=serv_client[area]["裁判文书"]
l_sxzx=serv_client[area]["失信被执行人"]
l_xzcf=serv_client[area]["行政处罚"]
l_gqdj=serv_client[area]["股权冻结"]

# 历史数据-------->历史法院公告  历史经营异常  历史限制消费 历史裁判文书  历史被执行人 历史失信被执行人  历史行政处罚  历史股权冻结
lh_fygg=serv_client[area]["历史法院公告"]
lh_jyyc=serv_client[area]["历史经营异常"]
lh_xzxf=serv_client[area]["历史限制消费"]
lh_cpws=serv_client[area]["历史裁判文书"]
lh_bzxr=serv_client[area]["历史被执行人"]
lh_sxzx=serv_client[area]["历史失信被执行人"]
lh_xzcf=serv_client[area]["历史行政处罚"]
lh_gqdj=serv_client[area]["历史股权冻结"]

local_sb = client[area]['商标信息']
local_zpzz = client[area]['作品著作权']
local_dxxk = client[area]['电信许可']
local_rzzq = client[area]['软著著作权']
local_xzxk = client[area]['行政许可']
local_zzzs = client[area]['资质证书']

"""redis"""
#过滤表
# 公司id   "filter:shandong:company_id"
filter=f"{area}:filter:company_id"

# 服务器数据  "shandong:filter:company"
serv_company=f"{area}:filter:company"




def init():
    init_map={
    
    }

