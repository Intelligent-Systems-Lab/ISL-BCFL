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
import ipfshttpclient

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

# class Model(nn.Module):
#     def __init__(self):
#         super().__init__()
#         self.hidden = nn.Linear(784, 20)
#         self.output = nn.Linear(20, 10)

#     def forward(self, x):
#         x = self.hidden(x)
#         x = torch.sigmoid(x)
#         x = self.output(x)
#         return x

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        
        self.cnn = nn.Sequential(nn.Conv2d(in_channels=1, out_channels=32, kernel_size=5),
                                     nn.ReLU(inplace=True),
                                     nn.Conv2d(in_channels=32, out_channels=32, kernel_size=5),
                                     nn.ReLU(inplace=True),
                                     nn.MaxPool2d(kernel_size=2),
                                     nn.Dropout(0.25),
                                     nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3),
                                     nn.ReLU(inplace=True),
                                     nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3),
                                     nn.ReLU(inplace=True),
                                     nn.MaxPool2d(kernel_size=2, stride=2),
                                     nn.Dropout(0.25))
        
        self.classifier = nn.Sequential(nn.Linear(576, 256),
                                       nn.Dropout(0.5),
                                       nn.Linear(256, 47))

        
    def forward(self, x):
        x = self.cnn(x)
        x = x.view(x.size(0), -1) # flatten layer
        x = self.classifier(x)
        
        return x

class Aggregator(aggregator_pb2_grpc.AggregatorServicer):
    def __init__(self):
        while True:
            try:
                self.client = ipfshttpclient.connect("/ip4/172.168.10.10/tcp/5001/http")
                break
            except:
                print("Waiting for ipfs services at : 172.168.10.10:5001")
                time.sleep(1)

    def aggregate(self, request, result):
        print("Training...")

        models = request.Models.split(",")

        realmodels = []
        for hm in models:
            print("Agg Download...")
            mod = self.client.cat(hm).decode()
            realmodels.append(mod)

        result = agg(realmodels)

        hashresult = self.client.add_str(result)

        return aggregator_pb2.AggResult(Round=request.Round, Result=hashresult)


def serve(port):
    print("Port : ",port)
    time.sleep(2)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    aggregator_pb2_grpc.add_AggregatorServicer_to_server(Aggregator(), server)

    server.add_insecure_port('0.0.0.0:'+port)
    server.start()
    server.wait_for_termination()

def agg(models):
    print("Len of models : ",len(models))
    model_list = []
    for m in models:
        #print("Append great?")
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