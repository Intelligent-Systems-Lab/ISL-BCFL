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

if [ "$ID" = "0" ]
then
    echo "Removing"
    rm -r /tenconfig/mytestnet
    cd /tenconfig
    tendermint testnet
fi

sleep 3

DATAPATH=/mountdata/$DATASET/"$DATASET"_train_$ID.csv

if [ "$MODE" = "core" ]
then
    export TMHOME="/tenconfig/mytestnet/node$ID"

    rm -r /root/logs
    mkdir -p /root/logs

    sed -i 's#laddr = "tcp://127.0.0.1:26657"#laddr = "tcp://0.0.0.0:26657"#'  $TMHOME/config/config.toml
    echo "Start"
    python -u /root/py-app/bcfl.py -config /root/py-app/config/config.ini &

    tendermint node --home $TMHOME --proxy_app "tcp://localhost:26658"

else 
    # sleep 2
    # rm -r /root/.tendermint
    # tendermint init
    # rm /root/.tendermint/config/config.toml
    # rm /root/.tendermint/config/genesis.json
    # cp /tenconfig/mytestnet/node0/config/config.toml /root/.tendermint/config
    # cp /tenconfig/mytestnet/node0/config/genesis.json /root/.tendermint/config

    # NODEID=$(python -c 'import random; print(random.randint(1,100000))')
    # sed -i "s#moniker = \"node0\"#moniker = \"node$NODEID\"#"  /root/.tendermint/config/config.toml
    # tendermint node --proxy_app kvstore
    python /root/py-app/bcfl.py -dataset $DATAPATH 
fi
