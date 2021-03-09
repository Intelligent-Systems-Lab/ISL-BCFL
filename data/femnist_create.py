import os, sys, json
from collections import defaultdict
from tqdm import tqdm
import numpy as np
import pandas as pd
import random
import math
import argparse

def get_dict_idx():
    d = {0:"label"}
    count = 1
    for i in range(1, 29):
        for j in range(1, 29):
            d[count] = "{}x{}".format(i, j)
            count += 1
    return d

def image_invert(img):
    return [int(255-i) for i in img]


def read_dir(data_dir):
    clients = []
    groups = []
    data = defaultdict(lambda : None)

    files = os.listdir(data_dir)
    files = [f for f in files if f.endswith('.json')]
    for f in tqdm(files):
        file_path = os.path.join(data_dir,f)
        with open(file_path, 'r') as inf:
            cdata = json.load(inf)
        clients.extend(cdata['users'])
        if 'hierarchies' in cdata:
            groups.extend(cdata['hierarchies'])
        data.update(cdata['user_data'])
    clients = list(sorted(data.keys()))
    return clients, groups, data

def image_invert(img):
    return [int(255-i) for i in img]


if __name__ == '__main__': 
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, default=None)
    parser.add_argument('--n', type=int, default=100, help="There are 3500 client in this dataset, we will random selected n client of it.")
    parser.add_argument('-f')
    
    args = parser.parse_args()
    
    if args.data is None:
        exit()

    path = args.data
    number_of_client = args.n

    train_path = os.path.join(path, "train")
    test_path = os.path.join(path, "test")

    os.mkdir(os.path.join(path, "iid"))
    os.mkdir(os.path.join(path, "niid"))
    os.mkdir(os.path.join(path, "niid","single_test"))
    
    print("Read data from : {}".format(train_path))    
    x_train, f_train, d_train = read_dir(train_path)
    
    print("Read data from : {}".format(test_path)) 
    x_test, f_test, d_test = read_dir(test_path)

    # [ [writer1, [[label, ...], [label, ...], [label, ...], ... ]],
    #   [writer2, [[label, ...], [label, ...], [label, ...], ... ]],
    #    . 
    #    .
    #    .
    # ]

    ########################################################################
    ## sample data from both train and test dataset ########################
    random_sample = random.sample(list(range(len(x_train))), k = number_of_client)
    
    # append smaped writer's name in the list
    train_sampled_list = []
    for i in range(len(random_sample)):
        train_sampled_list.append([x_train[i],[]])

    test_sampled_list = train_sampled_list.copy()
    
    ########################################################################
    ## append niid training image into list and save #######################
    for i in range(len(train_sampled_list)):
        writer = train_sampled_list[i][0]
        images = []
        for j in range(len(d_train[writer]["y"])):
            label = [d_train[writer]["y"][j]]
            image = image_invert(d_train[writer]["x"][j])
            label = [int(i) for i in label]
            img = label+image
            images.append(img)
        train_sampled_list[i][1].extend(images)

    
    # save train non-iid data to csv files
    niid_path = os.path.join(path, "niid")
    print("Save train niid data to : {}".format(niid_path))
    for p in tqdm(range(len(train_sampled_list))):
        df = pd.DataFrame(data=train_sampled_list[p][1])
        df = df.rename(columns=get_dict_idx())
        save_path = os.path.join(niid_path, "femnist_train_{}.csv".format(p))
        df.to_csv(save_path, mode='w', index=False)

    ########################################################################
    ## append niid test image into list and save mix and single ############
    for i in range(len(test_sampled_list)):
        writer = test_sampled_list[i][0]
        images = []
        for j in range(len(d_test[writer]["y"])):
            label = [d_test[writer]["y"][j]]
            image = image_invert(d_test[writer]["x"][j])
            label = [int(i)]
            img = label+image
            images.append(img)
        test_sampled_list[i][1].extend(images)

    niid_path = os.path.join(path, "niid", "single_test")
    print("Save test niid single data to : {}".format(niid_path))
    for p in tqdm(range(len(test_sampled_list))):
        df = pd.DataFrame(data=test_sampled_list[p][1])
        df = df.rename(columns=get_dict_idx())
        save_path = os.path.join(niid_path, "femnist_single_{}.csv".format(p))
        df.to_csv(save_path, mode='w', index=False)
    

    # mix 
    # [[label, ...], [label, ...], [label, ...], ... ]
    test_sampled_mix = []
    for i in range(len(test_sampled_list)):
        for j in test_sampled_list[i][1]:
            test_sampled_mix.append(j)
    random.shuffle (test_sampled_mix)

    # save test non-iid data to csv files
    niid_path = os.path.join(path, "niid")
    save_path = os.path.join(niid_path, "femnist_test.csv")
    print("Save test niid data to : {}".format(save_path))
    df = pd.DataFrame(data=test_sampled_mix)
    df = df.rename(columns=get_dict_idx())
    df.to_csv(save_path, mode='w', index=False)

    ########################################################################
    ## append iid train image into list and save ###########################

    iid_all_list = []

    for i in range(62):
        iid_all_list.append([])
    
    for i in range(len(train_sampled_list)):
        for j in train_sampled_list[i][1]:
                iid_all_list[j[0]].append(j)
    
    packages = []
    num_package = number_of_client
    for i in range(num_package):
        list_of_containt = []
        for k in range(62):
            Xp = iid_all_list[k]
            u = math.ceil(len(Xp) / num_package) * i
            d = math.ceil(len(Xp) / num_package) * (i + 1)
            if i == (num_package - 1):
                list_of_containt = list_of_containt + iid_all_list[k][u:len(Xp)]
            else:
                list_of_containt = list_of_containt + iid_all_list[k][u:d]
        random.shuffle(list_of_containt)
        packages.append(list_of_containt)

    iid_path = os.path.join(path, "iid")
    print("Save train iid data to : {}".format(iid_path))
    for p in tqdm(range(len(packages))):
        df = pd.DataFrame(data=packages[p])
        df = df.rename(columns=get_dict_idx())
        save_path = os.path.join(iid_path, "femnist_train_{}.csv".format(p))
        df.to_csv(save_path, mode='w', index=False)


    ########################################################################
    ## append iid test image into list and save ############################
    
    # test data is the same

    # save test non-iid/iid data to csv files
    iid_path = os.path.join(path, "iid")
    save_path = os.path.join(iid_path, "femnist_test.csv")
    print("Save test iid data to : {}".format(save_path))
    df = pd.DataFrame(data=test_sampled_mix)
    df = df.rename(columns=get_dict_idx())
    df.to_csv(save_path, mode='w', index=False)


    ########################################################################
    ## append non-iid all image into list and save #########################

    # same as iid training dataset

    niid_all = []
    for i in iid_all_list:
        niid_all.extend(i)

    random.shuffle(niid_all)

    niid_path = os.path.join(path, "niid")
    save_path = os.path.join(niid_path, "femnist_train.csv")
    print("Save train non-iid data to : {}".format(save_path))
    df = pd.DataFrame(data=niid_all)
    df = df.rename(columns=get_dict_idx())
    df.to_csv(save_path, mode='w', index=False)

    ########################################################################
    ## append iid all image into list and save #############################

    iid_all = []
    for i in iid_all_list:
        iid_all.extend(i)

    random.shuffle(iid_all)

    iid_path = os.path.join(path, "iid")
    save_path = os.path.join(iid_path, "femnist_train.csv")
    print("Save train iid data to : {}".format(save_path))
    df = pd.DataFrame(data=iid_all)
    df = df.rename(columns=get_dict_idx())
    df.to_csv(save_path, mode='w', index=False)

    print("Done")
