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

from aggregator import aggregator
from trainer import trainer
from db import db as moddb
from tx_handler import tx as sender

state = {
    "Round": 0,
    "AggWeight": [],
    "BaseResult": "",
    "IncomingModel": [],
}

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
            atx["Param"]["Result"] = tx_["Param"]["Result"]
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

    def __init__(self, trainer, aggregator, states_, threshold_):
        self.trainer = trainer
        self.aggregator = aggregator
        self.states = states_
        self.threshold = threshold_

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
        log.info("Got ChectTx : {}".format(tx))

        data = eval(tx.decode())
        log.info(data)
        tx_ = tx_checker(data["Type"], data)
        if tx_ is None:
            return ResponseCheckTx(code=1)  # reject code != 0

        if data["Type"] == "aggregation":
            if self.aggregator.aggergateCheck(data["Param"]):
                return ResponseCheckTx(code=CodeTypeOk)
        elif data["Type"] == "update":
            pass
        return ResponseCheckTx(code=CodeTypeOk)

    def deliver_tx(self, tx) -> ResponseDeliverTx:
        """Simply increment the state"""
        # value = decode_number(tx)
        # self.txCount += 1
        # log.info("Got DeliverTx w/ {}, so txCount increase to {}".format(value, self.txCount))
        data = eval(tx.decode())

        if data["Type"] == "aggregation":
            # add to base_list
            if self.aggregator.aggergateCheck(data["Param"]):
                sta = state.copy()
                sta["Round"] = data["Param"]["Round"]
                sta["AggWeight"] = data["Param"]["Weight"]
                sta["BaseResult"] = data["Param"]["Result"]
                self.states.append(sta)
                self.trainer.trainRun(data["Param"]["Result"], data["Param"]["Round"])
            else:
                return ResponseDeliverTx(code=1)
        elif data["Type"] == "update":
            if self.states[-1]["Round"] == data["Param"]["Round"]:
                self.states[-1]["IncomingModel"].append(data["Param"]["Weight"])
                if len(self.states[-1]["IncomingModel"]) >= self.threshold:
                    self.aggregator.aggergateRun(self.states[-1]["IncomingModel"], self.states[-1]["Round"])
            else:
                return ResponseDeliverTx(code=1)
        else:
            return ResponseDeliverTx(code=1)
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
    parser.add_argument('-dataset', type=str, default=None, help='Path to dataset')
    args = parser.parse_args()

    newsender = sender()
    newdb = moddb("ipfs")
    newagg = aggregator(log, newdb, newsender)
    newtrain = trainer(log, args.dataset, newdb, newsender)

    states = []
    threshold = 4
    # Create the app
    app = ABCIServer(app=SimpleBCFL(newtrain, newagg, states, threshold), port=args.p)
    # Run it
    app.run()
