import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader, TensorDataset, Dataset
from torch.utils.data.sampler import SubsetRandomSampler
from torch import optim
import pandas as pd
import sys
import time
from concurrent import futures
import logging
import grpc
import argparse
import base64
import io
import ipfshttpclient


class trainer:
    def __init__(self, dataset, ipfsHandler, devices="CPU", batchsize=1024, ):
        self.dataset = dataset  # path to dataset
        self.devices = devices
        self.batchsize = batchsize
        self.ipfsHandler = ipfsHandler

    def training(self):
        pass
