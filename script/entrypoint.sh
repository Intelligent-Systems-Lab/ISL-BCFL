#!/bin/bash

echo "  ___ ___ _      _      _   ___  "
echo " |_ _/ __| |    | |    /_\ | _ ) "
echo "  | |\__ \ |__  | |__ / _ \| _ \ "
echo " |___|___/____| |____/_/ \_\___/ "
echo
echo

echo
echo "RUN!!!!"
# read -p "Press [Enter] to continue... or [Control + c] to stop..."
sleep 1

if [ "$MODE" != "" ]
then
    echo -e "\n[Mode] $MODE"
    sleep 1
else
    echo -e "\nPlease set env MODE"
    exit
fi
sleep 1

if [ -f "/tendermint/mytestnet" ]
then
    echo "Init tendermint node env."
    sleep 2
    mkdir -p /tendermint/mytestnet
    cd /tendermint/mytestnet
    tendermint testnet
else 
    echo "/tendermint/mytestnet exist"
fi


export TMHOME="/tendermint/mytestnet/node$ID"

if [ "$MODE" = "node" ]
then
    tendermint node --home $TMHOME --proxy_app "tcp://abci$ID:26658"
else
    cd 
    #bash grpcsetup.sh
    #cd ~/trainer
    #make build_proto
    echo "run app"
    mkdir -p $GOPATH/src/github.com/isl/bcflapp/proto
    cp  /root/app/* $GOPATH/src/github.com/isl/bcflapp
    cp  /root/trainer/proto/*.pb.go $GOPATH/src/github.com/isl/bcflapp/proto
    cd $GOPATH/src/github.com/isl/bcflapp
    go mod init github.com/isl/bcflapp
    echo "Building..."
    rm $GOPATH/src/github.com/isl/bcflapp/proto/go*
    go build -o ticket main.go ticketstore.go type.go aggregator.go trainer.go
    # go build -o ticket ./...
    ./ticket -config /tendermint/mytestnet/node$ID
fi

# TX=$(base64 tx.txt)
# curl --header "Content-Type: application/json" -X POST --data "{\"jsonrpc\":\"2.0\", \"method\": \"broadcast_tx_sync\", \"params\": [\"$TX\"], \"id\": 1}" localhost:26657