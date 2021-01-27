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

if [ "$ID" = "0" ]
then
    echo "Removing"
    rm -r /tenconfig/mytestnet
    cd /tenconfig
    tendermint testnet
fi

sleep 5

# if [ -f "/tendermint/mytestnet" ]
# then
#     echo "Init tendermint node env."
#     sleep 2
#     mkdir -p /tendermint/mytestnet
#     cd /tendermint/mytestnet
#     #tendermint testnet
#     unzip mytestnet.zip
# else 
#     echo "/tendermint/mytestnet exist"
# fi





if [ "$MODE" = "core" ]
then
    export TMHOME="/tenconfig/mytestnet/node$ID"

    if [ -f "/tenconfig/mytestnet/logs" ]
    then
        mkdir -p /tenconfig/mytestnet/logs
    fi
    sed -i 's#laddr = "tcp://127.0.0.1:26657"#laddr = "tcp://0.0.0.0:26657"#'  $TMHOME/config/config.toml
    echo "Start"
    tendermint node --home $TMHOME --proxy_app kvstore
else 
    sleep 2
    rm -r /root/.tendermint
    tendermint init
    rm /root/.tendermint/config/config.toml
    rm /root/.tendermint/config/genesis.json
    cp /tenconfig/mytestnet/node0/config/config.toml /root/.tendermint/config
    cp /tenconfig/mytestnet/node0/config/genesis.json /root/.tendermint/config

    NODEID=$(python -c 'import random; print(random.randint(1,100000))')
    sed -i "s#moniker = \"node0\"#moniker = \"node$NODEID\"#"  /root/.tendermint/config/config.toml
    tendermint node --proxy_app kvstore
fi
