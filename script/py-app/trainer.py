import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader, TensorDataset, Dataset
from torch.utils.data.sampler import SubsetRandomSampler
from torch import optim
import argparse
import base64
import io, os
import ipfshttpclient
import time
import thread_handler as th
from messages import AggregateMsg, UpdateMsg

from utils import *


def train(logger, dbHandler, bmodel, _round, sender, dataloader, device="GPU"):
    logger.info("Train start")
    # model = Model()
    # model = base642fullmodel(dbHandler.cat(bmodel))
    #
    # optimizer = optim.RMSprop(model.parameters(), lr=0.001)
    # loss_function = nn.CrossEntropyLoss()
    # if (device == "GPU"):
    #     model.cuda()
    #
    # model.train()
    # for data, target in dataloader:
    #     if (device == "GPU"):
    #         data = data.cuda()
    #         target = target.cuda()
    #
    #     optimizer.zero_grad()
    #     # data = data.view(data.size(0),-1)
    #
    #     output = model(data.float())
    #
    #     loss = loss_function(output, target)
    #
    #     loss.backward()
    #
    #     optimizer.step()
    #
    # if (device == "GPU"):
    #     model.cpu()
    #
    # dbres = dbHandler.add(fullmodel2base64(model))
    UpdateMsg.set_cid(0)

    result = UpdateMsg()
    result.set_round()
    result.set_weight("models")
    # time.sleep(3)
    send_result = sender.send(result.json_serialize())
    logger.info("Train done")
    return send_result


class trainer:
    def __init__(self, logger, dataset, dbHandler, sender, devices="CPU", batchsize=1024):
        self.logger = logger
        # self.dataset = dataset  # path to dataset
        self.devices = devices
        self.batchsize = batchsize
        self.dbHandler = dbHandler

        # self.dataloader = getdataloader(dataset)
        self.dataloader = None
        self.sender = sender

    def trainRun(self, bmodel_, round_):
        t = th.create_job(train, (self.logger, self.dbHandler, bmodel_, round_, self.sender, self.dataloader))
        t.start()
        self.logger.info("Run done")

    # def trainRun(self, bmodel):
    #     print("Run train")
