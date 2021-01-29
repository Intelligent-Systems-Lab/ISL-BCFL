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
import random


def train(logger, dbHandler, bmodel, _round, sender, dataloader, device="GPU"):
    logger.info("Train start1")
    model = Model()
    logger.info("Train start2")
    try:
        logger.info("Train start3")
        model = base642fullmodel(dbHandler.cat(bmodel))
        # logger.info("ipfs success : {}".format(model[:20]))
    except KeyboardInterrupt:
        logger.info("ipfs fail")
    logger.info("Train model resolved")
    optimizer = optim.RMSprop(model.parameters(), lr=0.001)
    loss_function = nn.CrossEntropyLoss()
    if device == "GPU":
        model.cuda()

    model.train()
    logger.info("Train model dataloader")
    for data, target in dataloader:
        if device == "GPU":
            data = data.cuda()
            target = target.cuda()

        optimizer.zero_grad()
        # data = data.view(data.size(0),-1)

        output = model(data.float())

        loss = loss_function(output, target)

        loss.backward()

        optimizer.step()

    if device == "GPU":
        model.cpu()

    dbres = dbHandler.add(fullmodel2base64(model))
    logger.info("Train model result")
    UpdateMsg.set_cid(0)

    result = UpdateMsg()
    result.set_round(_round)
    result.set_weight(dbres)
    result.set_cid(os.getenv("ID"))
    # time.sleep(3)
    logger.info("Train send")
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
        self.logger.info("Load dataset...")
        self.dataloader = getdataloader(dataset)
        # self.dataloader = None
        self.sender = sender

    def trainRun(self, bmodel_, round_):
        t = th.create_job(train, (self.logger,
                                  self.dbHandler,
                                  bmodel_,
                                  round_,
                                  self.sender,
                                  self.dataloader,
                                  self.devices))
        t.start()
        self.logger.info("Run done")

    # def trainRun(self, bmodel):
    #     print("Run train")
