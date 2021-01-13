# How to push first base-model as TX

```bash=
cd {path to ISL-BCFL}/script/trainer

# This first base model that had upload to ipfs.
IPFSMOD=$(ipfs --api /ip4/0.0.0.0/tcp/5001 add ./firstMOD.txt -q)
echo $IPFSMOD


# Encode TX into base64 
TX=$(python3 -c "import base64,sys; print(base64.b64encode(sys.argv[1].encode('UTF-8')).decode('UTF-8'))" "{\"round\":0,\"weight\":\"$IPFSMOD\",\"cid\":0}")
echo $TX

# Post TX
curl --header "Content-Type: application/json" -X POST --data "{\"jsonrpc\":\"2.0\", \"method\": \"broadcast_tx_sync\", \"params\": [\"$TX\"], \"id\": 1}" localhost:26657
```
