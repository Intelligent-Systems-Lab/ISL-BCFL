import sys

import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader, TensorDataset, Dataset
from torch.utils.data.sampler import SubsetRandomSampler
from torch import optim
import sys
import time
from concurrent import futures
import logging

import argparse
import base64
import io, os
import ipfshttpclient
import thread_handler as th
from messages import AggregateMsg, UpdateMsg
import random
from utils import *
from models.eminst_model import *


def aggergate(logger, dbHandler, models, _round, sender):
    logger.info("Agg start")
    logger.info("Len of models : {}".format(len(models)))
    model_list = []
    for m in models:
        model = Model()
        model = base642fullmodel(dbHandler.cat(m))
        model_list.append(model)

    new_model_state = model_list[0].state_dict()

    # sum the weight of the model
    for m in model_list[1:]:
        state_m = m.state_dict()
        for key in state_m:
            new_model_state[key] += state_m[key]

    # average the model weight
    for key in new_model_state:
        new_model_state[key] /= len(model_list)

    new_model = model_list[0]
    new_model.load_state_dict(new_model_state)

    dbres = dbHandler.add(fullmodel2base64(new_model))

    AggregateMsg.set_cid(os.getenv("ID"))

    result = AggregateMsg()
    result.set_round(_round+1)
    result.set_weight(models)
    result.set_result(dbres)
    # result.set_cid(os.getenv("ID"))
    send_result = sender.send(result.json_serialize())
    logger.info("Agg done")
    return send_result


class aggregator:
    def __init__(self, logger, dbHandler, sender):
        self.logger = logger
        self.dbHandler = dbHandler
        self.sender = sender

    def aggergate_run(self, bmodels, round_):
        t = th.create_job(aggergate, (self.logger, self.dbHandler, bmodels, round_, self.sender))
        t.start()
        self.logger.info("Run Agg")

    def aggergate_check(self, modtx) -> bool:
        rou = modtx["Round"]
        wei = modtx["Weight"]
        return True

    def aggergate_manager(self, txmanager, tx):
        if tx["type"] == "aggregate_again" or (tx["type"] == "update" and len(txmanager.get_incoming_model()) >= txmanager.threshold):
            txmanager.aggregation_lock = True
            if self.aggregator_selection(txmanager, txmanager.states[-1].selection_nonce) == os.getenv("ID"):
                self.aggergate_run(txmanager.get_incoming_model(), txmanager.get_last_round())
        else:
            return

    def aggregator_selection(self, txmanager, nonce = 0, num_of_validator = 4):
        return hash(txmanager.get_last_base_model + str(nonce))%num_of_validator

