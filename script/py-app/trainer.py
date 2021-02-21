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
# from models.eminst_model import *
from models.mnist_fedavg import *
import random


def train(logger, dbHandler, bmodel, _round, sender, dataloader, device="GPU"):
    model = Model()
    try:
        # print(type(dbHandler.cat(bmodel)))
        model = base642fullmodel(dbHandler.cat(bmodel))
        # logger.info("ipfs success : {}".format(model[:20]))
    except KeyboardInterrupt:
        logger.info("ipfs fail")
    # logger.info("Train model resolved")
    if device == "GPU":
        model.cuda()

    optimizer = get_optimizer(model=model, lr=0.01)
    loss_function = get_criterion(device=device)

    model.train()
    # logger.info("Train model dataloader")
    for i in range(10):
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
    # logger.info("Train model result")
    # UpdateMsg.set_cid(os.getenv("ID"))

    result = UpdateMsg()
    result.set_cid(os.getenv("ID"))
    result.set_round(_round)
    result.set_weight(dbres)
    # result.set_cid(os.getenv("ID"))
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
        self.logger.info("Use : {}".format(self.devices))
        self.batchsize = batchsize
        self.dbHandler = dbHandler
        self.dataloader = getdataloader(dataset)
        # self.dataloader = None
        self.sender = sender
        self.last_train_round = -1

    def train_run(self, bmodel_, round_):
        t = th.create_job(train, (self.logger,
                                  self.dbHandler,
                                  bmodel_,
                                  round_,
                                  self.sender,
                                  self.dataloader,
                                  self.devices))
        t.start()
        self.logger.info("Run done")

    def train_manager(self, txmanager, tx):
        if tx["type"] == "aggregation" or tx["type"] == "create_task":
            incomings = txmanager.get_last_state()["incoming_model"]
            try:
                cids = [i["cid"] for i in incomings]
            except:
                cid = []
            if not os.getenv("ID") in cids and self.last_train_round + 1 == txmanager.get_last_round():
                self.logger.info("star training")
                txmanager.aggregation_lock = False
                self.train_run(txmanager.get_last_base_model(), txmanager.get_last_round())
                self.last_train_round = txmanager.get_last_round()

        else:
            return

    # def trainRun(self, bmodel):
    #     print("Run train")
