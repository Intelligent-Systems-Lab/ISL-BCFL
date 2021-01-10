
echo 'Initialize IPFS ...'
ipfs init
ipfs config Addresses.API /ip4/0.0.0.0/tcp/5001
ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080
echo 'Removing default bootstrap nodes...'
ipfs bootstrap rm --all