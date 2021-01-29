import struct
import abci.utils as util
import argparse
import json

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
from state_controller import State_controller
from utils import Model

log = util.get_logger()


def encode_number(value):
    return struct.pack('>I', value)


def decode_number(raw):
    return int.from_bytes(raw, byteorder='big')


class SimpleBCFL(BaseApplication):
    def __init__(self, controller):
        self.controller = controller

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
        log.info("Got ChectTx  {}".format(tx))
        value = eval(tx.decode())
        # log.info(value)
        if not self.controller.tx_checker(value):
            return ResponseCheckTx(code=1)  # reject code != 0
        log.info("Check ok")
        # log.info("Check ok")
        # log.info("Check ok")
        # log.info("Check ok")

        # if data["Type"] == "aggregation":
        #     if self.aggregator.aggergateCheck(data["weight"]):
        #         return ResponseCheckTx(code=CodeTypeOk)

        return ResponseCheckTx(code=CodeTypeOk)

    def deliver_tx(self, tx) -> ResponseDeliverTx:
        """Simply increment the state"""
        # value = decode_number(tx)
        # self.txCount += 1
        # log.info("Got DeliverTx {}, so txCount increase to {}".format(tx))
        log.info("Got DeliverTx  {}".format(tx))
        value = eval(tx.decode())
        # log.info(value)

        self.controller.tx_manager(value)
        log.info("Delivery ok")

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
    parser.add_argument('-device', type=str, default="CPU", help='Device')
    args = parser.parse_args()

    newsender = sender(log, url_="http://node0:26657")
    newdb = moddb("ipfs")
    newagg = aggregator(log, newdb, newsender)
    newtrain = trainer(log, args.dataset, newdb, newsender, devices=args.device)

    newcontroller = State_controller(log, newtrain, newagg, 4)

    # Create the app
    app = ABCIServer(app=SimpleBCFL(newcontroller), port=args.p)
    # Run it
    app.run()
