import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data.sampler import SubsetRandomSampler
import pandas as pd
import sys
sys.path.append('./proto')
import trainer_pb2
import trainer_pb2_grpc

from concurrent import futures
import logging
import grpc
import argparse  

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


class Aggregator(trainer_pb2_grpc.AggregatorServicer):
    def __init__(self, csvdata):
        self.dloader = getdataloader(csvdata)
        
    def Aggregate(self, request, result):
        #print(request.BaseModel)
        #print("training")
        result = trainOneEp(request.BaseModel, self.dloader)
        return trainer_pb2.TrainResult(Round=1, BaseModelResult=result)


def serve(data):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    trainer_pb2_grpc.add_AggregatorServicer_to_server(Aggregator(data), server)

    server.add_insecure_port('localhost:62287')
    server.start()
    server.wait_for_termination()

def trainOneEp(bmodel, dloader):
    model = base642fullmodel(bmodel)

    loss_function = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, weight_decay= 1e-6, momentum = 0.9, nesterov = True)
    
    model.train()
    for data, target in dloader: 

        optimizer.zero_grad()
        data = data.view(data.size(0),-1)

        output = model(data)

        loss = loss_function(output, target)

        loss.backward()              

        optimizer.step()
        train_loss.append(loss.item())

    model.eval() 

    bmodel_ = fullmodel2base64(model)

    return bmodel_

    
def getdataloader(dset = '/Users/tonyguo/Documents/github_project/ISL-BCFL/data/mnist/mnist_train_4.csv'):
    train = pd.read_csv(dset)
    
    train_labels = train_df['label'].values 
    train_data = train.drop(labels = ['label'], axis = 1)
    train_data = train_data.values.reshape(-1,28, 28)

    train_images_tensor = torch.tensor(train_data)/255.0
    train_labels_tensor = torch.tensor(train_labels)
    mnist = TensorDataset(train_images_tensor, train_labels_tensor)

    trainloader = DataLoader(mnist, batch_size=256, shuffle= True)

    return trainloader



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default=None)
    parser.add_argument('-f')
    args = parser.parse_args()

    logging.basicConfig()
    serve(args.data)
