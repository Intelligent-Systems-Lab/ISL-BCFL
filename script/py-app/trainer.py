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


def train(logger, dbHandler, local_ep, bmodel, _round, sender, dataloader, device, lr, opti):
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

    optimizer = get_optimizer(opti, model=model, lr=lr)
    loss_function = get_criterion(device=device)

    model.train()
    # logger.info("Train model dataloader")
    for i in range(local_ep):
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
    def __init__(self, logger, config, dbHandler, sender, devices="CPU", batchsize=1024):

        # if self.config.trainer.get_dataset() == "mnist":
        #     from models.mnist_model import *
        # elif self.config.trainer.get_dataset() == "mnist_fedavg":
        #     from models.mnist_fedavg import *
        # elif self.config.trainer.get_dataset() == "emnist":
        #     from models.eminst_model import *
        # elif self.config.trainer.get_dataset() == "emnist_fedavg":
        #     from models.emnist_fedavg import *

        self.logger = logger
        self.config = config
        # self.dataset = dataset  # path to dataset
        self.devices = self.config.trainer.get_device()
        self.logger.info("Use : {}".format(self.devices))
        self.local_bs = self.config.trainer.get_local_bs()
        self.local_ep = self.config.trainer.get_local_ep()
        self.dbHandler = dbHandler
        self.dataloader = getdataloader(self.config.trainer.get_dataset(), batch=self.local_bs)
        # self.dataloader = None
        self.sender = sender
        self.last_train_round = -1
        
        self.lr = self.config.trainer.get_lr()
        self.optimizer = self.config.trainer.get_optimizer()

    def train_run(self, bmodel_, round_):
        t = th.create_job(train, (self.logger,
                                  self.dbHandler,
                                  self.local_ep,
                                  bmodel_,
                                  round_,
                                  self.sender,
                                  self.dataloader,
                                  self.devices,
                                  self.lr,
                                  self.optimizer
                                  ))
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
