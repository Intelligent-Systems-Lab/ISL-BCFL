import struct
import abci.utils as util
import argparse

from abci import (
    ABCIServer,
    BaseApplication,
    ResponseInfo,
    ResponseInitChain,
    ResponseCheckTx,
    ResponseDeliverTx,
    ResponseQuery,
    ResponseCommit,
    CodeTypeOk,
)

import aggregator
import trainer

# TX :
aggTx = {"Type": "aggregation",
         "Param": {
             "Round": 0,
             "Weight": ["<hash>", "<hash>"],
             "Result": "<hash>",
             "Cid": 0,
         },
         "MaxIteration": 100,
         "Sample": 0.5,
         }
updateTx = {"Type": "update",
            "Param": {
                "Round": 0,
                "Weight": "<hash>",
                "Cid": 0,
            },
            "MaxIteration": 100,
            "Sample": 0.5,
            }

log = util.get_logger()


def tx_checker(type_, tx_):
    atx = None
    if type_ == "aggregation":
        atx = aggTx.copy()
        try:
            atx["Type"] = tx_["Type"]
            atx["Param"]["Round"] = tx_["Param"]["Round"]
            atx["Param"]["Weight"] = tx_["Param"]["Weight"]
            atx["Param"]["Cid"] = tx_["Param"]["Cid"]
            atx["MaxIteration"] = tx_["MaxIteration"]
            atx["Sample"] = tx_["Sample"]
        except:
            return None
    elif type_ == "update":
        atx = updateTx.copy()
        try:
            atx["Type"] = tx_["Type"]
            atx["Param"]["Round"] = tx_["Param"]["Round"]
            atx["Param"]["Weight"] = tx_["Param"]["Weight"]
            atx["Param"]["Cid"] = tx_["Param"]["Cid"]
            atx["MaxIteration"] = tx_["MaxIteration"]
            atx["Sample"] = tx_["Sample"]
        except:
            return None
    return atx


def encode_number(value):
    return struct.pack('>I', value)


def decode_number(raw):
    return int.from_bytes(raw, byteorder='big')


class SimpleBCFL(BaseApplication):

    def __init__(self, trainer, aggregator):
        self.trainer = trainer
        self.aggregator = aggregator

    def info(self, req) -> ResponseInfo:
        """
        Since this will always respond with height=0, Tendermint
        will resync this app from the begining
        """
        r = ResponseInfo()
        r.version = "1.0"
        r.last_block_height = 0
        r.last_block_app_hash = b''
        return r

    def init_chain(self, req) -> ResponseInitChain:
        """Set initial state on first run"""
        log.info("Got InitChain")
        self.txCount = 0
        self.last_block_height = 0
        return ResponseInitChain()

    def check_tx(self, tx) -> ResponseCheckTx:
        """
        Validate the Tx before entry into the mempool
        Checks the txs are submitted in order 1,2,3...
        If not an order, a non-zero code is returned and the tx
        will be dropped.
        """
        # log.info("Got ChectTx : {}".format(tx))

        data = eval(tx.decode())
        log.info(data)
        tx_ = tx_checker(data["Type"], data)
        if tx_ is None:
            return ResponseCheckTx(code=1)  # reject code != 0

        if data["Type"] == "aggregation":
            if self.aggregator.aggergateCheck():
                return ResponseCheckTx(code=CodeTypeOk)
        elif data["Type"] == "update":
            pass
        return ResponseCheckTx(code=CodeTypeOk)

    def deliver_tx(self, tx) -> ResponseDeliverTx:
        """Simply increment the state"""
        value = decode_number(tx)
        self.txCount += 1
        log.info("Got DeliverTx w/ {}, so txCount increase to {}".format(value, self.txCount))
        return ResponseDeliverTx(code=CodeTypeOk)

    def query(self, req) -> ResponseQuery:
        """Return the last tx count"""
        v = encode_number(self.txCount)
        return ResponseQuery(code=CodeTypeOk, value=v, height=self.last_block_height)

    def commit(self) -> ResponseCommit:
        """Return the current encode state value to tendermint"""
        log.info("Got Commit")
        hash = struct.pack('>Q', self.txCount)
        return ResponseCommit(data=hash)


if __name__ == '__main__':
    # Define argparse argument for changing proxy app port
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', type=int, default=26658, help='Proxy app port')
    args = parser.parse_args()

    newagg = aggregator()
    newtrain = trainer()

    # Create the app
    app = ABCIServer(app=SimpleBCFL(newtrain, newagg), port=args.p)
    # Run it
    app.run()
