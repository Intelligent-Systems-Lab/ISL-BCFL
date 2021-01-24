import sys

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


class aggregator:
    def __init__(self, ipfsHandler):
        self.ipfsHandler = ipfsHandler

    def aggergate(self):
        pass
