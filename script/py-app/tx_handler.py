import base64

import requests
import json
from utils import Upper_TX_formater, Lower_TX_formater

data = {"round": 0,
        "weight": "$IPFSMOD",
        "cid": 0
        }

exampleTX = {"jsonrpc": "2.0",
             "method": "broadcast_tx_sync",
             "params": [],
             "id": 1
             }
exampleParams = {"type": "aggregation",
                 "Param": {},
                 "MaxIteration": 100,
                 "Sample": 0.5,
                 }

exampleAgg = {"Round": 0,
              "Weight": ["<hash>", "<hash>"],
              "Result": "<hash>",
              "Cid": 0,
              }

exampleupdate = {"Round": 0,
                 "Weight": "<hash>",
                 "Cid": 0,
                 }


class tx:
    def __init__(self, url_="http://172.17.0.3:26657"):
        self.url = url_
        self.headers = {'content-type': 'application/json'}

    def send(self, data_) -> str:
        payload_ = exampleTX.copy()
        data_ = json.dumps(Upper_TX_formater(eval(data_)))
        tx_ = base64.b64encode(data_.encode()).decode()
        print("tx: ", tx_)
        payload_['params'] = [tx_]
        print("payload: ", json.dumps(payload_))
        response = requests.post(self.url, data=json.dumps(payload_), headers=self.headers)
        return response

