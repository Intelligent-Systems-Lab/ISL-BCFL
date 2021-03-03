from multiprocessing import Pool
import time, json, requests
import sys, os, base64
import argparse
import subprocess
sys.path.append('script/py-app')
import ipfshttpclient
import glob
from options import Configer
from tqdm import tqdm

#############################################
def run_ipfs_container():
    proc = subprocess.Popen('docker-compose -f ./docker-compose-pygpu.yml up ipfsA', shell=True, stdout=subprocess.PIPE)
    return proc

def run_network_container():
    proc = subprocess.Popen('docker-compose -f ./docker-compose-pygpu.yml up tshark', shell=True, stdout=subprocess.PIPE)
    return proc

def run_vlaidatror_nodes_container():
    proc = subprocess.Popen('docker-compose -f ./docker-compose-pygpu.yml up node0 node1 node2 node3', shell=True, stdout=subprocess.PIPE)
    return proc

def run_nodes_container(nodes):
    proc = subprocess.Popen('docker-compose -f ./docker-compose-pygpu.yml scale nodes={}'.format(nodes), shell=True, stdout=subprocess.PIPE)
    return proc

def run_eval_container():
    proc = subprocess.Popen('docker run --gpus all --rm -it -v {}:/root/:z -v {}:/mountdata/ --network isl-bcfl_localnet tony92151/py-abci python3 -u /root/py-app/eval/eval.py -config /root/py-app/config/config.ini'.format(os.path.abspath("./script"), os.path.abspath("./data")), shell=True, stdout=subprocess.PIPE)
    return proc
#############################################
def send_create_task_TX(max_iteration=10):
    proc = subprocess.Popen('docker run --rm -it -v {}:/root/:z tony92151/py-abci python3 /root/py-app/utils.py -config /root/py-app/config/config.ini > FIRSTMOD.txt'.format(os.path.abspath("./script")), shell=True)
    proc.wait()

    time.sleep(1)
    client = ipfshttpclient.connect("/ip4/0.0.0.0/tcp/5001/http")

    ipfs_model = client.add_str(open(os.path.abspath("./FIRSTMOD.txt"), "r").read())
    print(ipfs_model) 

    param = json.loads('{"type": "create_task","max_iteration": "","aggtimeout": 10,"weight":""}')
    param["max_iteration"] = max_iteration
    param["weight"] = ipfs_model

    b64payload = base64.b64encode(json.dumps(param).encode('UTF-8')).decode('UTF-8')
    print(b64payload)
    
    url = "http://localhost:26657"
    payload = json.loads('{"jsonrpc":"2.0", "method": "broadcast_tx_sync", "params": "", "id": 1}')
    payload["params"] = [b64payload]

    # Adding empty header as parameters are being sent in payload
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(json.dumps(json.loads(r.content), indent=4, sort_keys=True))
    return proc

def set_config_file(f):
    proc = subprocess.Popen("cp {} {}/config_run.ini".format(f, os.path.dirname(f)), shell=True)
    return proc

def stop_network_container():
    proc = subprocess.Popen('docker-compose -f ./docker-compose-py.yml stop tshark', shell=True, stdout=subprocess.PIPE)
    return proc

def terminate_all_container():
    proc = subprocess.Popen('docker-compose -f ./docker-compose-pygpu.yml down -v', shell=True, stdout=subprocess.PIPE)
    return proc
#############################################
# def run_network_analyzer():
#     python network_analysiser.py $(pwd)/network_08_13_34.pcap $(pwd)/pcap.jpg $(pwd)/pcap2.jpg
#     proc = subprocess.Popen(, shell=True, stdout=subprocess.PIPE)
#     return proc

def move_result_to_save_folder(path):
    _ = subprocess.Popen('mv ./script/py-app/result.jpg {}'.format(path), shell=True, stdout=subprocess.PIPE)
    _ = subprocess.Popen('mv ./script/py-app/config/config_run.ini {}'.format(path), shell=True, stdout=subprocess.PIPE)
    _ = subprocess.Popen('mv ./script/py-app/*.json {}'.format(path), shell=True, stdout=subprocess.PIPE)
    _ = subprocess.Popen('mv ./network/*.pcap {}'.format(path), shell=True, stdout=subprocess.PIPE)
    # _ = subprocess.Popen('mv ./network/pcap*.jpg {}'.format(path), shell=True, stdout=subprocess.PIPE)
    _ = subprocess.Popen('rm -rf ./script/py-app/save', shell=True, stdout=subprocess.PIPE)

    # move 
    # return proc
#############################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help="path to config", type=str, default=None)
    parser.add_argument('--output', help="output", type=str, default=None)
    args = parser.parse_args()

    if args.config is None or args.output is None:
        print("Please set --config & --output.")
        exit()

    con_path = os.path.abspath(args.config)
    outpath_path = os.path.abspath(args.output)

    if not os.path.exists(outpath_path):
        os.makedirs(outpath_path)

    print("Read config: {}".format(con_path))
    con = Configer(con_path)

    # set up config file
    p_config = set_config_file(con_path)

    # # launch ipfs container
    p_ipfs = run_ipfs_container()
    print("PID : ipfs : {}".format(p_ipfs.pid))
    time.sleep(1)

    # # launch network capture container
    # p_net = run_network_container()
    # print("PID : network : {}".format(p_net.pid))
    # time.sleep(1)

    # launch network capture container
    p_vnodes = run_vlaidatror_nodes_container()
    print("PID : vlaidatror_nodes : {}".format(p_vnodes.pid))
    time.sleep(5)

    # # launch scalble-nodes container
    if not con.bcfl.get_scale_nodes() == 0:
        print("Scale node : {}".format(con.bcfl.get_scale_nodes()))
        p_snodes = run_nodes_container(con.bcfl.get_scale_nodes())
        print("PID : scale_nodes : {}".format(p_snodes.pid))
        time.sleep(1)

    # make sure all node are sycn done
    time.sleep(30)

    #send create-task TX to strat trining.
    send_create_task_TX(con.trainer.get_max_iteration())

    # check whether training process is finish
    path = os.path.abspath("./script/py-app/save/")
    if not os.path.exists(path):
        os.mkdir(path)

    check = 0
    for i in tqdm(range(con.trainer.get_max_iteration())):
        time.sleep(0.5)
        while True:
            l = len(glob.glob(path+"/*")) 
            if l>check:
                check+=1
                break
            else:
                time.sleep(5)

    # close run_network_container
    # _ = stop_network_container()
    # time.sleep(10)

    # launch eval container
    p_eval = run_eval_container()
    p_eval.wait()
    print("Eval done.\n")

    # run network analyzer
    # _ = run_network_analyzer()

    

    # terminate all container
    time.sleep(10)
    p_t = terminate_all_container()
    p_t.wait()

    # move all result to save_path
    p_save = move_result_to_save_folder(outpath_path)
    print("Done.\n")
