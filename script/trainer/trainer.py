import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader, TensorDataset, Dataset
from torch.utils.data.sampler import SubsetRandomSampler
from torch import optim
import pandas as pd
import sys
sys.path.append('./proto')
import trainer_pb2
import trainer_pb2_grpc
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
                                       nn.Linear(256, 10))

        
    def forward(self, x):
        x = self.cnn(x)
        x = x.view(x.size(0), -1) # flatten layer
        x = self.classifier(x)
        
        return x



class Trainer(trainer_pb2_grpc.TrainerServicer):
    def __init__(self, csvdata):
        self.dloader = getdataloader(csvdata)
        while True:
            try:
                self.client = ipfshttpclient.connect("/ip4/172.168.10.10/tcp/5001/http")
                break
            except:
                print("Waiting for ipfs services at : 172.168.10.10:5001")
                time.sleep(1)

    def Train(self, request, result):
        #print(request.BaseModel)
        print("Training...")
        result = trainOneEp(self.client.cat(request.BaseModel).decode(), self.dloader)
        hashresult = self.client.add_str(result)
        return trainer_pb2.TrainResult(Round=request.Round, Result=hashresult)


def serve(data, port):
    print("Read dataset : ",data)
    print("Port : ",port)
    time.sleep(2)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    trainer_pb2_grpc.add_TrainerServicer_to_server(Trainer(data), server)

    server.add_insecure_port('0.0.0.0:'+port)
    server.start()
    server.wait_for_termination()

def trainOneEp(bmodel, dloader):
    #return bmodel
    model = Model()
    model = base642fullmodel(bmodel)
    #return fullmodel2base64(model)
    print(model)
    # loss_function = nn.CrossEntropyLoss()
    # optimizer = optim.SGD(model.parameters(), lr=0.005)
    optimizer = optim.RMSprop(model.parameters(), lr=0.001)
    loss_function = nn.CrossEntropyLoss()

    model.train()
    for data, target in dloader:

        optimizer.zero_grad()
        #data = data.view(data.size(0),-1)

        output = model(data.float())

        loss = loss_function(output, target)

        loss.backward()

        optimizer.step()

    #model.eval()
    #print(model)
    bmodel_ = fullmodel2base64(model)
    #print(bmodel_)
    return bmodel_


# def getdataloader(dset = '/home/tedbest/Documents/mnist_train_0.csv'):
#     #print(dset)
#     train = pd.read_csv(dset)

#     train_labels = train['label'].values
#     train_data = train.drop(labels = ['label'], axis = 1)
#     train_data = train_data.values.reshape(-1,28, 28)

#     train_images_tensor = torch.tensor(train_data)/255.0
#     train_labels_tensor = torch.tensor(train_labels)
#     mnist = TensorDataset(train_images_tensor, train_labels_tensor)

#     trainloader = DataLoader(mnist, batch_size=256, shuffle= True)

#     return trainloader
class MNISTDataset(Dataset):
    """MNIST dataset"""
    
    def __init__(self, feature, target=None, transform=None):
        
        self.X = feature
        self.y = target
            
        self.transform = transform
    
    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        # training
        if self.transform is not None:
            return self.transform(self.X[idx]), self.y[idx]
        # testing
        elif self.y is None:
            return [self.X[idx]]
        # validation
        return self.X[idx], self.y[idx]

def getdataloader(dset = './mnist_test.csv'):
    #print(dset)
    train = pd.read_csv(dset)

    train_labels = train['label'].values
    train_data = train.drop(labels = ['label'], axis = 1)
    train_data = train_data.values.reshape(-1,28, 28)
    
    featuresTrain = torch.from_numpy(train_data)
    targetsTrain = torch.from_numpy(train_labels)
    
    data_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.RandomAffine(degrees=45, translate=(0.1, 0.1), scale=(0.8, 1.2)),
        transforms.ToTensor()]
        )

    train_set = MNISTDataset(featuresTrain.float(), targetsTrain, transform=data_transform)
    
    trainloader = torch.utils.data.DataLoader(train_set, batch_size = 256, shuffle = True)
    return trainloader



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default="/home/tedbest/Documents/mnist_train_0.csv")
    parser.add_argument('--port', type=str, default="63387")
    parser.add_argument('-f')
    args = parser.parse_args()

    logging.basicConfig()
    serve(args.data, args.port)