import json

import redis

serv_conn = redis.Redis(host='139.9.70.234', port=6379, db=2, password="anbo123", socket_connect_timeout=170)

# with open("config.json" ,"r" ,encoding="utf-8") as file:
#     config = file.read()
# config = json.loads(config)
#
# aa=config["fAddr"]
#
# for keys in aa:
#     serv_conn.set(keys,json.dumps(aa[keys]))
# serv_conn.set("localSAddr",json.dumps(["167",27017]))
# serv_conn.set("servSAddr",json.dumps(["234",12700,"root","QuyHlxXhW2PSHTwT","admin"]))




