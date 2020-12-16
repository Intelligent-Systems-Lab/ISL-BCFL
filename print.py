import torch
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--path", help="path of model")
args = parser.parse_args()

model = torch.jit.load(args.path)
print(model.state_dict()['conv1.bias'])