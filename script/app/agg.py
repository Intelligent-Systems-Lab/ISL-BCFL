import os
# import torch
import argparse
import base64
import sys
import io

import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader
from torch.utils.data.sampler import SubsetRandomSampler


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


model_list = []

f = open(sys.argv[1], "r")

models = f.read().split(",")

f.close()

print(models)

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

print(output)
