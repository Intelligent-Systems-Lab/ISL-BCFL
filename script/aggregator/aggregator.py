import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data.sampler import SubsetRandomSampler
from torch import optim
import pandas as pd
import sys
sys.path.append('./proto')
import aggregator_pb2
import aggregator_pb2_grpc
import time
from concurrent import futures
import logging
import grpc
import argparse
import base64
import io

torch.nn.Module.dump_patches = True

def fullmodel2base64(model):
    buffer = io.BytesIO()
    torch.save(model, buffer)
    bg = buffer.getvalue()
    return base64.b64encode(bg).decode()

def base642fullmodel(modbase64):
    inputrpc = bytes(modbase64.encode())
    inputrpc_ = base64.b64decode(inputrpc)
    loadmodel = torch.load(io.BytesIO(inputrpc_))
    return loadmodel

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.hidden = nn.Linear(784, 20)
        self.output = nn.Linear(20, 10)

    def forward(self, x):
        x = self.hidden(x)
        x = torch.sigmoid(x)
        x = self.output(x)
        return x



class Aggregator(aggregator_pb2_grpc.AggregatorServicer):
    # def __init__(self, csvdata):
    #     self.dloader = getdataloader(csvdata)

    def aggregate(self, request, result):
        print("Training...")

        models = request.Models.split(",")
        result = agg(models)

        return aggregator_pb2.AggResult(Round=1, Result=result)


def serve(port):
    print("Port : ",port)
    time.sleep(2)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    aggregator_pb2.add_AggregatorServicer_to_server(Aggregator(), server)

    server.add_insecure_port('0.0.0.0:'+port)
    server.start()
    server.wait_for_termination()

def agg(models):
    for m in models:
        model_list.append(base642fullmodel(m))

    new_model_state = model_list[0].state_dict()

    #sum the weight of the model
    for m in model_list[1:]:
        state_m = m.state_dict()
        for key in state_m:
            new_model_state[key] += state_m[key]

    #average the model weight
    for key in new_model_state:
        new_model_state[key] /= len(model_list)


    new_model = model_list[0]
    new_model.load_state_dict(new_model_state)

    output = fullmodel2base64(new_model)

    return output
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=str, default="63387")
    parser.add_argument('-f')
    args = parser.parse_args()

    logging.basicConfig()
    serve(args.port)