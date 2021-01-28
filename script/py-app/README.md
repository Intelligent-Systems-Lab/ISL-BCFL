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

## Send create-task TX
```bash=
IPFSMOD=$(ipfs --api /ip4/0.0.0.0/tcp/5001 add ./firstMOD.txt -q)
echo $IPFSMOD


# Encode TX into base64 
TX=$(python3 -c "import base64,sys; print(base64.b64encode(sys.argv[1].encode('UTF-8')).decode('UTF-8'))" "{\"type\": \"create_task\",\"max_iteration\": 100,\"sample\": 0.5}",\"weight\":\"$IPFSMOD\"}")
echo $TX

curl --header "Content-Type: application/json" -X POST --data "{\"jsonrpc\":\"2.0\", \"method\": \"broadcast_tx_sync\", \"params\": [\"$TX\"], \"id\": 1}" localhost:26657
```