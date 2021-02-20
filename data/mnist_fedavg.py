import os                                                                       
import sys                                                                      
import struct                                                                   
import argparse                                          
import pandas as pd
import random
import math
import numpy as np



parser = argparse.ArgumentParser()
parser.add_argument('--data', type=str, default=None)
parser.add_argument('--n', type=int, default=5)
parser.add_argument('--format', type=str, default='csv',help="[csv, pickle]")
parser.add_argument('-f')

args = parser.parse_args()


X = pd.read_csv(args.data + "/mnist_train.csv")
num_package = args.n
# X_test = pd.read_csv("/Users/tonyguo/Desktop/mnist/mnist-in-csv/mnist_test.csv")

X_df = pd.DataFrame(X)

Xf_all_list = []

for i in range(10):
    Xi = X_df[X_df["label"] == i ].reset_index()
    Xf_all_list.append(Xi)
    
Xl_all_list = []

for i in range(10):
    Xl_list = [*range(1,len(Xf_all_list[i]),1)]
    random.shuffle(Xl_list)
    Xl_all_list.append(Xl_list)

packages = []

for i in range(num_package):
    list_of_containt = []
    for k in range(10):
        Xp = Xl_all_list[k]
        u = math.floor(len(Xp)/num_package)*i
        d = math.floor(len(Xp)/num_package)*(i+1)
        if i == (num_package-1):
            list_of_containt.append(Xf_all_list[k].iloc[Xl_all_list[k][u:]])
        else:
            list_of_containt.append(Xf_all_list[k].iloc[Xl_all_list[k][u:d]])
    packages.append(list_of_containt)

for p in range(len(packages)):
    pk = pd.concat(packages[p])
    pk = pk.sample(frac=1).reset_index(drop=True)
    del pk["index"]
    if args.format == "pickle":
        save_path = args.data+"/mnist_train_{}.p".format(p)
        print("Create : mnist_train_{}.p".format(p))
        pk.to_pickle(save_path)
    else:
        save_path = args.data+"/mnist_train_{}.csv".format(p)
        print("Create : mnist_train_{}.csv".format(p))
        pk.to_csv(save_path,mode = 'w', index=False)
    