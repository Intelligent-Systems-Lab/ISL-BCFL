import time
import uuid
from abci.utils import get_logger
import db as dbs

MODE = "ipfs"

if MODE == "ipfs":
    import ipfshttpclient

log = get_logger()


class db:
    def __init__(self, mode="ipfs"):
        if mode == "ipfs":
            self.db_ = dbs.ipfs(addr="/ip4/172.168.10.10/tcp/5001/http")
        elif mode == "...":
            pass
        else:
            pass

    def add(self, data):
        return self.db_.add(data)

    def cat(self, data):
        return self.db_.cat(data)
