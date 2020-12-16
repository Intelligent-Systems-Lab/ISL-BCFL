import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.datasets import MNIST
from torch.utils.data import DataLoader
from torch.utils.data.sampler import SubsetRandomSampler
from torch import optim
import numpy as np

import requests
import json
import time
import base64
import io
import signal

url = "http://localhost:4000/jsonrpc"

# Example echo method
payload = {
    "method": "abci_info",
    "jsonrpc": "2.0",
    "id": 0,
}
response = requests.post(url, json=payload).json()

inputrpc = response['result']['response']['data']['model']

def signal_handler(signal, frame):
        global interrupted
        interrupted = True

        
_tasks = transforms.Compose([
        transforms.ToTensor(), 
        transforms.Normalize(mean=(0.5,), std=(0.5,))
        ])

mnist = MNIST("data", download=True, train=True, transform=_tasks)

split = int(0.2 * len(mnist))
index_list = list(range(len(mnist)))
train_idx, valid_idx = index_list[:split], index_list[split:]

tr_sampler = SubsetRandomSampler(train_idx)
val_sampler = SubsetRandomSampler(valid_idx)

trainloader = DataLoader(mnist, batch_size=256, sampler=tr_sampler) 
validloader = DataLoader(mnist, batch_size=256, sampler=val_sampler)

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.hidden = nn.Linear(784, 128)
        self.output = nn.Linear(128, 10)
    
    def forward(self, x):
        x = self.hidden(x)
        x = torch.sigmoid(x)
        x = self.output(x)
        return x    

interrupted = False
signal.signal(signal.SIGINT, signal_handler)


def training_one(rpcmodel):
    model = Model()
    
    loss_function = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.01, weight_decay= 1e-6, momentum = 0.9, nesterov = True)
    inputrpc = bytes(rpcmodel.encode())
    inputrpc_ = base64.b64decode(inputrpc)
    model.load_state_dict(torch.load(io.BytesIO(inputrpc_)))
    
    model.train()
    for data, target in trainloader: 

        optimizer.zero_grad()
        data = data.view(data.size(0),-1)

        output = model(data)

        loss = loss_function(output, target)

        loss.backward()              

        optimizer.step()
        train_loss.append(loss.item())

    model.eval() 
    torch.save(model.state_dict(), "/tmp/mnist_tmp.pt")
    binfile = open("./mnist.pt","rb")
    c1 = base64.b64encode(binfile.read())
    binfile.close()
    return str(c1.decode())


def check():
    global old_round
    global old_inputrpc_
    
    payload_c = {
    "method": "abci_info",
    "jsonrpc": "2.0",
    "id": 0,
    }
    response = requests.post(url, json=payload_c).json()
    inputrpc_ = response['result']['response']['data']['model']
    round_ = response['result']['response']['data']['round']
    if old_round == round_:
        return False
    else:
        old_round = round_
        old_inputrpc_ = inputrpc_
        return True
    
def broadcast(newmodel):    
    payload_b = {
    "method": "broadcast_tx_sync",
    "jsonrpc": "2.0",
    "params": [newmodel],
    "id": 0,
    }
    response = requests.post(url, json=payload_b).json()
    gethash = response['result']['hash']
    
    return gethash
    

    
old_round = ""
old_inputrpc_ = ""

print("Init.")  
check()

while True:
    print(">>> Pending.")
    if check():
        print(">>> New model collected.")
        print(">>> Training.")
        result = training_one(old_inputrpc_)
        #result = "123"
    else:
        result = None
        
    if result!= None:
        print(">>> Broadcasting.")
        print(">>> Hash: ",broadcast(result))

    if interrupted:
        print("<< Exiting... >>")
        break
    else:
        time.sleep(3)
