FROM python:3.6.12

#RUN apk add --no-cache git make bash gcc musl-dev jq

# RUN mkdir /installiipfs &&\
#     cd /installiipfs &&\
#     wget https://github.com/ipfs/go-ipfs/releases/download/v0.7.0/go-ipfs-source.tar.gz &&\
#     mkdir -p $GOPATH/src/github.com/ipfs/go-ipfs &&\
#     tar zxvf go-ipfs-source.tar.gz -C $GOPATH/src/github.com/ipfs/go-ipfs &&\
#     cd $GOPATH/src/github.com/ipfs/go-ipfs &&\
#     make install

RUN apt-get update && apt-get -y upgrade &&\
    pip3 install --upgrade pip setuptools &&\
    pip3 install protobuf &&\
    pip3 install grpcio &&\
    pip3 install grpcio-tools &&\
    pip3 install pandas

RUN wget https://download.pytorch.org/whl/cu100/torch-1.2.0-cp36-cp36m-manylinux1_x86_64.whl &&\
    pip install torch-1.2.0-cp36-cp36m-manylinux1_x86_64.whl &&\
    rm torch-1.2.0-cp36-cp36m-manylinux1_x86_64.whl &&\
    pip3 install torchvision==0.4.0
