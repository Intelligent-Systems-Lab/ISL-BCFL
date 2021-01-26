#!/bin/bash
sleep 8

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

if [ "$MODE" = "core" ]
then
    tendermint node --home $TMHOME --proxy_app "tcp://abci$ID-gpu:26658"
else
    DATAPATH=/mountdata/$DATASET/"$DATASET"_train_$ID.csv
    python3 /root/bcfl.py -dataset $DATAPATH
fi
