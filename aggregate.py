import os
import torch
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--path", help="path to the model list file")
parser.add_argument("--save_path", help="path to save the new model")

args = parser.parse_args()
model_list = []

for m in os.listdir(args.path):
    model_list.append(torch.jit.load(args.path+m))

new_model_state = model_list[0].state_dict()

#sum the weight of the model
for m in model_list[1:]:
    state_m = m.state_dict()
    for key in state_m:
        new_model_state[key] += state_m[key]

#average the model weight
for key in new_model_state:
    new_model_state[key] /= len(model_list)

    
new_model = torch.jit.load(args.path + os.listdir(args.path)[0])
new_model.load_state_dict(new_model_state)


x = torch.rand(64, 1, 28, 28)
torch.jit.save(torch.jit.trace(new_model, x), args.save_path + "new_model.pt")

print("new_model saved")
