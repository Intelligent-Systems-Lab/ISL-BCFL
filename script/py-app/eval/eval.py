import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader, TensorDataset, Dataset
from torch.utils.data.sampler import SubsetRandomSampler
from torch import optim
import pandas as pd
import sys

sys.path.append('/root')

import time
import numpy as np
from concurrent import futures
import logging
import grpc
import argparse
import base64
import io
import matplotlib.pyplot as plt 
from tqdm import tqdm
import json 
import ipfshttpclient

from models.eminst_model import Model, getdataloader
from utils import *


def acc_plot(models, dataloder, device="CPU"):
    accd = []
    for model in tqdm(models):
        ans = np.array([])
        res = np.array([])
        if device == "GPU":
            model.cuda()
        
        model.eval()
        for data, target in dataloder:
            #data = data.view(data.size(0),-1)
            data = data.float()
            if device == "GPU":
                data = data.cuda()

            output = model(data)

            _, preds_tensor = torch.max(output, 1)
            preds = np.squeeze(preds_tensor.cpu().numpy())
            ans = np.append(ans, np.array(target))
            res = np.append(res, np.array(preds))

        acc = (ans==res).sum()/len(ans)
        accd.append(acc)
        
    return accd

def local_training(dataloder, device="CPU"):
    model = Model()
    optimizer = optim.RMSprop(model.parameters(), lr=0.001)
    loss_function = nn.CrossEntropyLoss()
    model.train()
    models = []
    for i in tqdm(range(100)):
        #print("E : ", i)
        running_loss = 0
        for data, target in dataloder:
            if device == "GPU":
                model.cuda() 
                data = data.cuda()
                target = target.cuda()
            optimizer.zero_grad()
            #data = data.view(data.size(0),-1)
            output = model(data.float())
            loss = loss_function(output, target)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        if device == "GPU":
            model.cpu()
        models.append(model.cpu())
    return models




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-dataset', type=str, default=None, help='Path to dataset folder')
    parser.add_argument('-result', type=str, default=None, help='Path to json result')
    parser.add_argument('-output', type=str, default=None, help='Output path')
    args = parser.parse_args()

    
    client = ipfshttpclient.connect("/ip4/140.113.164.150/tcp/5001/")

    file = open(args.result,'r')
    context = json.load(file)
    file.close()
    lcontext = []
    for i in context["data"]:
        lcontext.append(i["base_result"])

    bcfl_models = []
    print("Download...")
    for i in lcontext:
        m = client.cat(i).decode()
        bcfl_models.append(base642fullmodel(m))

    print("Prepare test dataloader...")
    test_dataloader = getdataloader(args.dataset+"/emnist_test.csv")

    bcfl_result = acc_plot(bcfl_models, test_dataloader, device = "GPU")

    print("Local training...\n")
    print("Prepare train dataloader...")
    train_dataloader = getdataloader(args.dataset+'/emnist_train_all.csv')

    local_models = local_training(train_dataloader, device = "GPU")

    local_result = acc_plot(local_models, test_dataloader, device = "GPU")

    plt.title("BCFL vs. Local training") 
    plt.grid(True)
    plt.ylabel("Accuracy")
    plt.xlabel("Round")
    #plt.plot(range(10), bcfl_acc[:10], range(10), local_acc[:10])
    plt.plot(range(100), bcfl_result[:100], color='red', label='BCFL')
    plt.plot(range(100), local_result[:100], color='green', label='LOCAL')
    plt.legend()

    # plt.show()
    plt.savefig(args.output)





