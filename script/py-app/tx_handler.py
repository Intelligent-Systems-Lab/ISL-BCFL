import base64

import requests
import json

data = {"round": 0,
        "weight": "$IPFSMOD",
        "cid": 0
        }

exampleTX = {"jsonrpc": "2.0",
             "method": "broadcast_tx_sync",
             "params": [],
             "id": 1
             }
exampleParams = {"Type": "aggregation",
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

    def sendagg(self, d, timeout=None, timeoutEvent=None) -> str:
        # tx = base64.b64encode(d.encode('UTF-8')).decode('UTF-8')
        payload_ = exampleTX.copy()
        eParams = exampleParams.copy()
        eParams["Type"] = "aggregation"

        param = exampleAgg.copy()
        param["Round"] = d["Round"]
        param["Weight"] = d["Weight"]
        param["Result"] = d["Result"]
        param["Cid"] = d["Cid"]

        eParams["Param"] = param

        print(eParams)

        tx = base64.b64encode(json.dumps(eParams).encode()).decode()
        print("tx: ", tx)
        print("eParams: ", json.dumps(eParams))

        payload_['params'] = [tx]
        print("payload_: ", json.dumps(payload_))
        response = requests.post(self.url, data=json.dumps(payload_), headers=self.headers)
        return response

    def sendupdate(self, d, timeout=None, timeoutEvent=None) -> str:
        payload_ = exampleTX.copy()
        eParams = exampleParams.copy()
        eParams["Type"] = "update"

        param = exampleupdate.copy()
        param["Round"] = d["Round"]
        param["Weight"] = d["Weight"]
        param["Cid"] = d["Cid"]

        eParams["Param"] = param
        print(eParams)

        tx = base64.b64encode(json.dumps(eParams).encode()).decode()
        payload_['params'] = [tx]
        response = requests.post(self.url, data=json.dumps(payload_), headers=self.headers)
        return response

    # def validator
