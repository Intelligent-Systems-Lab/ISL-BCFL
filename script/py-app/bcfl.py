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

# Tx encoding/decoding
from abci.utils import get_logger

log = get_logger()


def encode_number(value):
    return struct.pack('>I', value)


def decode_number(raw):
    return int.from_bytes(raw, byteorder='big')


class SimpleCounter(BaseApplication):

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
        log.info("Got ChectTx w/ {}".format(tx))
        value = decode_number(tx)
        if not value == (self.txCount + 1):
            # respond with non-zero code
            log.warn("\tInconsistent Tx Value {}, txCount={}".format(value,self.txCount))
            return ResponseCheckTx(code=1)
        return ResponseCheckTx(code=CodeTypeOk)

    def deliver_tx(self, tx) -> ResponseDeliverTx:
        """Simply increment the state"""
        value = decode_number(tx)
        self.txCount += 1
        log.info("Got DeliverTx w/ {}, so txCount increase to {}".format(value,self.txCount))
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
    parser.add_argument('-p', type=int, default=26657, help='Proxy app port')
    args = parser.parse_args()

    # Create the app
    app = ABCIServer(app=SimpleCounter(), port=args.p)
    # Run it
    app.run()
