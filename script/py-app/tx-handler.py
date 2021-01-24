import requests
import json

payload = {
    "method": "abci_info",
    "jsonrpc": "2.0",
    "id": 0,
}


class tx:
    def __init__(self, url_="http://localhost:4000/jsonrpc"):
        self.url = url_

    def send(self, timeout=False, timeoutBlock=3, timeoutEvent=None) -> str:
        payload_ = payload.copy()
        payload_['method'] = 1
        # if timeout:
        response = requests.post(self.url, json=payload).json()
        return "ok"
