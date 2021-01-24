import sys


class trainer:
    def __init__(self, dataset, ipfsHandler, devices="CPU", batchsize=1024, ):
        self.dataset = dataset  # path to dataset
        self.devices = devices
        self.batchsize = batchsize
        self.ipfsHandler = ipfsHandler

    def training(self):
        pass
