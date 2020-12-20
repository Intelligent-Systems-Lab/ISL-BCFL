
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
    mkdir -p /tendermint/mytestnet
    cd /tendermint/mytestnet
    tendermint testnet
fi


export TMHOME="/tendermint/mytestnet/node$ID"

if [ "$MODE" = "node" ]
then
    tendermint node --home $TMHOME --proxy_app "tcp://abci$ID:26658"
else
    echo "run app"
    mkdir -p $GOPATH/src/github.com/me/example
    cp /root/app/* $GOPATH/src/github.com/me/example
    cd $GOPATH/src/github.com/me/example
    go mod init github.com/me/example
    echo "Building..."
    go build -o ticket main.go ticketstore.go
    ./ticket
fi
