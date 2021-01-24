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