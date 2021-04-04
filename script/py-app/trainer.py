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
import copy
import thread_handler as th
from messages import AggregateMsg, UpdateMsg

from utils import *
# from models.eminst_model import *
from models.models_select import *
import random


def train(logger, dbHandler, config, bmodel, _round, sender, dataloader):
    local_ep = config.trainer.get_local_ep()
    device = config.trainer.get_device()
    lr = config.trainer.get_lr()

    if config.trainer.get_dataset() == "mnist":
        Model = Model_mnist
    elif config.trainer.get_dataset() == "mnist_fedavg":
        Model = Model_mnist_fedavg
    elif config.trainer.get_dataset() == "femnist":
        Model = Model_femnist
    # model_ = Model()

    model = Model()
    if type(bmodel) == str:
        try:
            model = base642fullmodel(dbHandler.cat(bmodel))
            # logger.info("ipfs success : {}".format(model[:20]))
        except TimeoutError:
            logger.info("ipfs fail")
    else:
        model = copy.deepcopy(bmodel)

    if device == "GPU":
        model.cuda()

    optimizer = get_optimizer(config.trainer.get_optimizer(), model=model, lr=lr, compress_ratio=config.dgc.get_compress_ratio())
    loss_function = get_criterion(config.trainer.get_lossfun(), device=device)

    if config.trainer.get_optimizer() == "DGCSGD":
        optimizer.memory.clean()

    model.train()
    # logger.info("Train model dataloader")
    local_g =[]
    for i in range(local_ep):
        if config.trainer.get_optimizer() == "DGCSGD":
            optimizer.memory.clean()
            
        for data, target in dataloader:
            if device == "GPU":
                data = data.cuda()
                target = target.cuda()

            optimizer.zero_grad()
            # data = data.view(data.size(0),-1)

            output = model(data.float())

            loss = loss_function(output, target)

            loss.backward()

            optimizer.gradient_collect()
            optimizer.step()

        # optimizer.compress(compress=False)
        # local_g.append(optimizer.decompress(optimizer.get_compressed_gradient()))

    if device == "GPU":
        model.cpu()

    # optimizer.memory.clean()
    # for i in local_g:
    #     optimizer.memory.mem.append(i)
    optimizer.compress(compress=True)
    cg = optimizer.get_compressed_gradient()

    dbres = dbHandler.add(object_serialize(cg))
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
    def __init__(self, logger, config, dbHandler, sender):
        self.logger = logger
        self.config = config
        # self.dataset = dataset  # path to dataset
        self.devices = self.config.trainer.get_device()
        self.logger.info("Use : {}".format(self.devices))
        self.local_bs = self.config.trainer.get_local_bs()
        # self.local_ep = self.config.trainer.get_local_ep()
        self.dbHandler = dbHandler

        dset = "/mountdata/{}/{}_train_<ID>.csv".format(self.config.trainer.get_dataset_path(), self.config.trainer.get_dataset()).replace("<ID>", os.getenv("ID"))
        self.dataloader = getdataloader(dset, batch=self.local_bs)
        # self.dataloader = None
        self.sender = sender
        self.last_train_round = -1

        # self.lr = self.config.trainer.get_lr()
        # self.optimizer = self.config.trainer.get_optimizer()

    def train_run(self, bmodel_, round_):
        t = th.create_job(train, (self.logger,
                                  self.dbHandler,
                                  self.config,
                                  bmodel_,
                                  round_,
                                  self.sender,
                                  self.dataloader
                                  ))
        t.start()
        self.logger.info("Run done")

    def train_manager(self, txmanager, tx):
        if tx["type"] == "aggregation" or tx["type"] == "create_task":
            incomings = txmanager.get_last_state()["incoming_gradient"]
            try:
                cids = [i["cid"] for i in incomings]
            except:
                cid = []
            if (not os.getenv("ID") in cids) and (self.last_train_round + 1 == txmanager.get_last_round()):
                self.logger.info("star training")
                txmanager.aggregation_lock = False
                self.train_run(txmanager.get_last_base_model(), txmanager.get_last_round())
                self.last_train_round = txmanager.get_last_round()

        else:
            return

    def opt_step_base_model(self, txmanager, base_gradient):
        # txmanager.get_last_gradient_result()
        if self.config.trainer.get_dataset() == "mnist":
            Model = Model_mnist
        elif self.config.trainer.get_dataset() == "mnist_fedavg":
            Model = Model_mnist_fedavg
        elif self.config.trainer.get_dataset() == "femnist":
            Model = Model_femnist
        # model_ = Model()

        model = Model()
        model = copy.deepcopy(txmanager.get_last_base_model())

        model.cpu().train()
        optimizer = get_optimizer(self.config.trainer.get_optimizer(), model=model, lr=self.config.trainer.get_lr(), compress_ratio=self.config.dgc.get_compress_ratio())
        # print("base_grad: {}".format(type(object_deserialize(self.dbHandler.cat(base_gradient)))))
        cg = optimizer.decompress(object_deserialize(self.dbHandler.cat(base_gradient)))
        # print("cg: {}".format(type(cg)))
        optimizer.set_gradient(cg)
        optimizer.step()
        return copy.deepcopy(model.cpu())

    def get_model_by_ipfs(self, key):
        if self.config.trainer.get_dataset() == "mnist":
            Model = Model_mnist
        elif self.config.trainer.get_dataset() == "mnist_fedavg":
            Model = Model_mnist_fedavg
        elif self.config.trainer.get_dataset() == "femnist":
            Model = Model_femnist
        # model_ = Model()

        model = Model()
        model = base642fullmodel(self.dbHandler.cat(key))
        # txmanager.set_last_base_model(model.cpu())
        
        return model
        


    # def trainRun(self, bmodel):
    #     print("Run train")
