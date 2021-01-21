# import sys
# sys.path.append('./')

import network_db_v1 as mdb
import traffic_capture



if __name__ == '__main__':
    addr = "mongodb://172.168.10.101:27017/"
    mondb = mdb.db(addr)


