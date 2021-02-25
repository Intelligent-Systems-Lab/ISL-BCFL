import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader, TensorDataset, Dataset
from torch.utils.data.sampler import SubsetRandomSampler
from torch import optim
import pandas as pd
import sys, copy

sys.path.append('/root/py-app')

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

from models.models_select import *
from utils import *

from options import Configer


def acc_plot(models, dataloder, device="CPU"):
    accd = []
    for model in tqdm(models):
        ans = np.array([])
        res = np.array([])
        if device == "GPU":
            model.cuda()

        model.eval()
        for data, target in dataloder:
            # data = data.view(data.size(0),-1)
            data = data.float()
            if device == "GPU":
                data = data.cuda()

            output = model(data)

            _, preds_tensor = torch.max(output, 1)
            preds = np.squeeze(preds_tensor.cpu().numpy())
            ans = np.append(ans, np.array(target))
            res = np.append(res, np.array(preds))

        acc = (ans == res).sum() / len(ans)
        accd.append(acc)

    return accd


def local_training(dataloder, con):
    dataset = con.trainer.get_dataset()
    device = con.trainer.get_device()
    iter_ep = con.trainer.get_max_iteration()
    loacl_ep = con.trainer.get_local_ep()
    lr = con.trainer.get_lr()

    if dataset == "mnist":
        Model = Model_mnist
    elif dataset == "mnist_fedavg":
        Model = Model_mnist_fedavg
    model_ = Model()
    # optimizer = optim.RMSprop(model_.parameters(), lr=0.001)
    # loss_function = nn.CrossEntropyLoss()
    # model_.train()
    models = []

    bmodel = fullmodel2base64(Model())
    for i in tqdm(range(iter_ep*loacl_ep)):
        model = base642fullmodel(bmodel)
        optimizer = optim.RMSprop(model.parameters(), lr=lr)
        loss_function = nn.CrossEntropyLoss()

        optimizer = get_optimizer(con.trainer.get_optimizer(), model=model, lr=lr)
        loss_function = get_criterion(con.trainer.get_lossfun(), device=device)

        if i % loacl_ep ==0:
            models.append(copy.deepcopy(model).cpu())
        # print("E : ", i)
        running_loss = 0
        for data, target in dataloder:
            if device == "GPU":
                model.train()
                model.cuda()
                data = data.cuda()
                target = target.cuda()
            optimizer.zero_grad()
            # data = data.view(data.size(0),-1)
            output = model(data.float())
            loss = loss_function(output, target)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            
        bmodel = fullmodel2base64(copy.deepcopy(model).cpu().eval())
        if device == "GPU":
            model_.cpu()
        #models.append(model_.cpu())
        #print(running_loss)
    return models


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument('-dataset', type=str, default=None, help='Path to dataset folder')
    # parser.add_argument('-result', type=str, default=None, help='Path to json result')
    # parser.add_argument('-output', type=str, default=None, help='Output path')
    # parser.add_argument('-ipfsaddr', type=str, default="/ip4/172.168.10.10/tcp/5001/", help='ipfs address')
    parser.add_argument('-config', type=str, default=None, help='config')
    args = parser.parse_args()

    if args.config is None:
        exit("No config.ini found.")

    con = Configer(args.config)

    client = ipfshttpclient.connect(con.eval.get_ipfsaddr())

    reuslt = "/root/py-app/{}_round_result_0.json".format(con.trainer.get_max_iteration())
    file_ = open(reuslt, 'r')
    context = json.load(file_)
    file_.close()
    lcontext = []
    for i in context["data"]:
        lcontext.append(i["base_result"])

    if con.trainer.get_dataset() == "mnist":
        Model = Model_mnist
    elif con.trainer.get_dataset() == "mnist_fedavg":
        Model = Model_mnist_fedavg
    else:
        print("No model match")
        exit()

    bcfl_models = []
    print("Download...")
    for i in lcontext:
        m = client.cat(i).decode()
        #model_ = Model()
        model_ = base642fullmodel(m)
        bcfl_models.append(copy.deepcopy(model_))
    print("Prepare test dataloader...")
    test_dataloader = getdataloader("/mountdata/{}/{}_test.csv".format(con.trainer.get_dataset(), con.trainer.get_dataset()), 512)

    bcfl_result = acc_plot(bcfl_models, test_dataloader, con.trainer.get_device())

    print("Local training...\n")
    print("Prepare train dataloader...")
    train_dataloader = getdataloader("/mountdata/{}/{}_train_0.csv".format(con.trainer.get_dataset(), con.trainer.get_dataset()), 512)

    local_models = local_training(train_dataloader, con)

    local_result = acc_plot(local_models, test_dataloader, con.trainer.get_device())

    plt.title(con.eval.get_title())
    plt.grid(True)
    plt.ylabel("Accuracy")
    plt.xlabel("Round")
    miter = con.trainer.get_max_iteration()
    # plt.plot(range(10), bcfl_acc[:10], range(10), local_acc[:10])
    plt.plot(range(miter), bcfl_result[:miter], color='red', label='BCFL')
    plt.plot(range(miter), local_result[:miter], color='green', label='LOCAL')
    plt.legend()

    # plt.show()
    plt.savefig(con.eval.get_output())
