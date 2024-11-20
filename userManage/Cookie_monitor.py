import json
import time
from redis import Redis,exceptions
from Login.LoginMonitor import SuccessCODE

local_VQ_conn = Redis(host='192.168.5.181', port=7933, db=0, password="fer@nhaweif576KUG",socket_connect_timeout=1170)

"""监控redis的cookies"""
def monitor_cookie():
    while True:
        try:
            keys=[{"searchCookie":"searchMobil"},{"detailCookie":"memeryUser"},{"sifaCookie":"sifaUser"},{"NoMemeryCookie":"LoginUser"}]
            for yy in keys:
                key=list(yy.keys())[0]
                key_len=local_VQ_conn.llen(key)
                if key_len>0:
                    print(key+" : "+str(key_len))
                else:
                    for _ in range(3):
                        try:
                            print(key)
                            res=local_VQ_conn.lpop(yy[key])
                            mobil=json.loads(res)
                            local_VQ_conn.rpush(yy[key],res)
                            print(mobil)
                            mobil["keys"]=yy[key]
                            SuccessCODE().main(mobil, 1, 80)
                        except Exception as e:
                            print(e)
                    time.sleep(20)
        except exceptions.ConnectionError as e:
            print(e)
            monitor_cookie()
            return
        except exceptions.TimeoutError as e:
            print(e)
            monitor_cookie()
            return


if __name__ == '__main__':
    monitor_cookie()
