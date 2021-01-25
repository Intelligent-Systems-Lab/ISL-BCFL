# py abci-app

## install abci lib
```bash=
gdown --id 15k8E-XuvcatKP1uFqv4pn3PignaKNMOv -O ./abci-0.6.1.tar.gz
tar zxvf abci-0.6.1.tar.gz

cd abci-0.6.1
python setup.py build
python setup.py install
cd ..

rm -r abci-0.6.1 abci-0.6.1.tar.gz
```

## Send TX
```bash=
IPFSMOD=$(ipfs --api /ip4/0.0.0.0/tcp/5001 add ./firstMOD.txt -q)
echo $IPFSMOD


# Encode TX into base64 
TX=$(python3 -c "import base64,sys; print(base64.b64encode(sys.argv[1].encode('UTF-8')).decode('UTF-8'))" "{\"Type\": \"aggregation\",\"Param\": {\"Round\": 0,\"Weight\": [],\"Result\": \"$IPFSMOD\",\"Cid\": 0,},\"MaxIteration\": 100,\"Sample\": 0.5}")
echo $TX

curl --header "Content-Type: application/json" -X POST --data "{\"jsonrpc\":\"2.0\", \"method\": \"broadcast_tx_sync\", \"params\": [\"$TX\"], \"id\": 1}" localhost:26657
```