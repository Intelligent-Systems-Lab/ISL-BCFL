import base64

import requests
import json

data = {"round": 0,
        "weight": "$IPFSMOD",
        "cid": 0
        }

p_send_tx = {"jsonrpc": "2.0",
             "method": "broadcast_tx_sync",
             "params": [],
             "id": 1
             }

class tx:
    def __init__(self, url_="http://localhost:4000/jsonrpc"):
        self.url = url_

    def send(self, d, timeout=None, timeoutEvent=None) -> str:
        tx = base64.b64encode(d.encode('UTF-8')).decode('UTF-8')
        payload_ = p_send_tx.copy()
        payload_['params'] = [tx]
        # if not (timeout == None):
        #     try:
        #         response = requests.post(self.url, data=payload_, timeout=timeout)
        #     except requests.Timeout:
        #         response = requests.post(self.url, data=payload_retrain, timeout=timeout)
        #     except requests.ConnectionError:
        #         pass
        # else:
        response = requests.post(self.url, json=payload_).json()
        return response
