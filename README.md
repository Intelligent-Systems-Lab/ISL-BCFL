# ISL-BCFL

## kvstore scable test
```bash=
docker-compose -f docker-compose-kvtest.yml up --scale nodes=5

docker-compose -f docker-compose-kvtest.yml down -v
```

now we move on to the python version app
# py abci-app

## dataset setup
```bash=
cd <path to repo>/data

# emnist dataset
NUMOFPKG=4 bash create_emnist_dataset.sh

# mnist
NUMOFPKG=4 bash create_mnist_dataset.sh
```
more detail in "data" folder.

## docker-compose run
```bash=
# CPU:
docker-compose -f ./docker-compose-py.yml up ipfsA
docker-compose -f ./docker-compose-py.yml up tshark
docker-compose -f ./docker-compose-py.yml up ipfsA node0 node1 node2 node3

docker-compose -f ./docker-compose-py.yml down -v

# GPU
docker-compose -f ./docker-compose-pygpu.yml up ipfsA 
docker-compose -f ./docker-compose-pygpu.yml up tshark
docker-compose -f ./docker-compose-pygpu.yml up ipfsA node0 node1 node2 node3

docker-compose -f ./docker-compose-pygpu.yml down -v
```

After training, terminate "tshark" program manually. The ```.pcap``` file will be saved in network folder.


## Send create-task TX
```bash=
# create new model
cd <path to repo>/script/py-app
docker run --rm -it -v $(pwd):/root/:z tony92151/py-abci python3 /root/utils.py /root/FIRSTMOD.txt
# sudo chown $(whoami)  FIRSTMOD.txt

# Upload to ipfs
IPFSMOD=$(ipfs --api /ip4/0.0.0.0/tcp/5001 add ./FIRSTMOD.txt -q)
echo $IPFSMOD

# Encode TX into base64 
TX=$(python3 -c "import base64,sys; print(base64.b64encode(sys.argv[1].encode('UTF-8')).decode('UTF-8'))" "{\"type\": \"create_task\",\"max_iteration\": 100,\"aggtimeout\": 8,\"weight\":\"$IPFSMOD\"}")
echo $TX

curl --header "Content-Type: application/json" -X POST --data "{\"jsonrpc\":\"2.0\", \"method\": \"broadcast_tx_sync\", \"params\": [\"$TX\"], \"id\": 1}" localhost:26657
```

## Evaluation

```bash=
cd <path to repo>
# This could take 50 minutes
docker run --gpus all --rm -it -v $(pwd)/script/py-app:/root/:z -v $(pwd)/data:/mountdata/ tony92151/py-abci python3 /root/eval/eval.py -dataset /mountdata/emnist -result /root/100_round_result_0.json -output /root/result.jpg
```

## Network analysis
```bash=
cd <path to repo>/network
python network_analysiser.py $(pwd)/network_08_13_34.pcap $(pwd)/pcap.jpg $(pwd)/pcap2.jpg
```


## Dependance

if you want to develope abci-application in pyhton, we have rebuild [davebryson/py-abci](https://github.com/davebryson/py-abci), and it work fine under tendermint > 0.34.0

### install py-abci lib
```bash=
gdown --id 15k8E-XuvcatKP1uFqv4pn3PignaKNMOv -O ./abci-0.6.1.tar.gz
tar zxvf abci-0.6.1.tar.gz

cd abci-0.6.1
python setup.py build
python setup.py install
cd ..

rm -r abci-0.6.1 abci-0.6.1.tar.gz
```