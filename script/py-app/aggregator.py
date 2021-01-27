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

from utils import *


def aggergate(logger, dbHandler, models, _round, sender):
    logger.info("Agg start")
    # logger.info("Len of models : ", len(models))
    # model_list = []
    # for m in models:
    #     model = Model()
    #     model = base642fullmodel(dbHandler.cat(m))
    #     model_list.append(model)
    #
    # new_model_state = model_list[0].state_dict()
    #
    # # sum the weight of the model
    # for m in model_list[1:]:
    #     state_m = m.state_dict()
    #     for key in state_m:
    #         new_model_state[key] += state_m[key]
    #
    # # average the model weight
    # for key in new_model_state:
    #     new_model_state[key] /= len(model_list)
    #
    # new_model = model_list[0]
    # new_model.load_state_dict(new_model_state)
    #
    # dbres = dbHandler.add(fullmodel2base64(new_model))

    result = AggregateMsg()
    result.set_sample(1)
    result.set_maxIteration(100)
    result.set_round(_round+1)
    result.set_weight(models)
    result.set_result("dbres")
    result.set_cid(0)

    send_result = sender.send(result.json_serialize())
    logger.info("Agg done")
    return send_result


class aggregator:
    def __init__(self, logger, dbHandler, sender):
        self.logger = logger
        self.dbHandler = dbHandler
        self.sender = sender

    def aggergateRun(self, bmodels, round_):
        t = th.create_job(aggergate, (self.logger, self.dbHandler, bmodels, round_, self.sender))
        t.start()
        self.logger.info("Run Agg")

    def aggergateCheck(self, modtx) -> bool:
        rou = modtx["Round"]
        wei = modtx["Weight"]
        return True
