import requests
import json
import time
import base64
import io
import signal

url = "http://localhost:26657"

# Example echo method
payload = {
  "method": "abci_query",
  "jsonrpc": "2.0",
  "params": {
    'path': 'bsemodel_state',
    'data': '',
    'height': '',
    'prove': 'false',
  },
}

payloadHeader = {
    'Content-Type': 'application/json',
}
response = requests.post(url, json=payload)

# inputrpc = response['result']['response']['value']

print(response)