FROM python:3.6.12

RUN apt-get update && apt-get -y upgrade &&\
    pip3 install --upgrade pip setuptools &&\
    pip install gdown &&\
    pip3 install ipfshttpclient==0.7.0a1

RUN gdown --id 15k8E-XuvcatKP1uFqv4pn3PignaKNMOv -O ./abci-0.6.1.tar.gz &&\
    tar zxvf abci-0.6.1.tar.gz &&\
    cd abci-0.6.1 &&\
    python setup.py install &&\
    cd .. &&\
    rm -r abci-0.6.1 abci-0.6.1.tar.gz

RUN wget https://download.pytorch.org/whl/cu100/torch-1.2.0-cp36-cp36m-manylinux1_x86_64.whl &&\
    pip install torch-1.2.0-cp36-cp36m-manylinux1_x86_64.whl &&\
    rm torch-1.2.0-cp36-cp36m-manylinux1_x86_64.whl &&\
    pip3 install torchvision==0.4.0