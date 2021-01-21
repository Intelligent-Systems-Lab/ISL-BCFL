# This script should monitor at eth0, capturing traffic.
# Network Traffic will be created in report folder.

# Author : Tony Guo
# Date : 18 Feb, 2021 

import numpy
import socket
import struct
import pymongo
from bson import ObjectId
import os, sys


class db:
    def __init__(self, dbhost="mongodb://localhost:27017/"):  # dbhost="localhost:27017/"
        self.myclient = pymongo.MongoClient(dbhost)
        self.mydb = self.myclient["traffic"]["capture"]

    def insert(self, data):
        # mydict = { "_id": 1, "name": "hello", "cn_name": "world"}
        x = self.mydb.insert_one(data)

        return x.inserted_id
    # def

def creatdata():
    pass


# if '__main__' == __name__:
#     mgdb = db()
#
#     a ="123"
#     b ="456"
#
#     kk = '{ "name":"'+a+'", "cn_name": "'+b+'"}'
#
#     da = eval(kk)
#     print(da)
#     re = mgdb.insert(da)
#     print(re)
    # Get time
    # print(ObjectId(re).generation_time)


