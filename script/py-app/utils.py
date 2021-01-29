import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader, TensorDataset, Dataset
from torch.utils.data.sampler import SubsetRandomSampler
from torch import optim
import pandas as pd
import sys
import time
from concurrent import futures
import logging
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


class MNISTDataset(Dataset):
    """MNIST dataset"""

    def __init__(self, feature, target, transform=None):

        self.X = []
        self.Y = target

        if transform is not None:
            for i in range(len(feature)):
                self.X.append(transform(feature[i]))

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):

        return self.X[idx], self.Y[idx]


def getdataloader(dset='./mnist_test.csv', batch=256):
    print("Dataset at : {}".format(dset))
    train = pd.read_csv(dset)

    train_labels = train['label'].values
    train_data = train.drop(labels=['label'], axis=1)
    train_data = train_data.values.reshape(-1, 28, 28)

    featuresTrain = torch.from_numpy(train_data)
    targetsTrain = torch.from_numpy(train_labels)

    data_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.RandomAffine(degrees=45, translate=(0.1, 0.1), scale=(0.8, 1.2)),
        transforms.ToTensor()]
    )

    train_set = MNISTDataset(featuresTrain.float(), targetsTrain, transform=data_transform)

    trainloader = torch.utils.data.DataLoader(train_set, batch_size=batch, shuffle=True, num_workers=4)
    return trainloader


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
        x = x.view(x.size(0), -1)  # flatten layer
        x = self.classifier(x)

        return x


if __name__ == "__main__":
    with open(sys.argv[1], "w") as file:
        file.write(fullmodel2base64(Model()))


