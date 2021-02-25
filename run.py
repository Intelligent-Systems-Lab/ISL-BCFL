from multiprocessing import Pool
import time
import sys, os
import argparse
import subprocess
sys.path.append('script/py-app')

from options import Configer

def run_ipfs_container():
    proc = subprocess.Popen('docker-compose -f ./docker-compose-pygpu.yml up ipfsA', shell=True, stdout=subprocess.PIPE)
    return proc

def run_network_container():
    proc = subprocess.Popen('docker-compose -f ./docker-compose-pygpu.yml up tshark', shell=True, stdout=subprocess.PIPE)
    return proc

def run_vlaidatror_nodes_container():
    proc = subprocess.Popen('docker-compose -f ./docker-compose-py.yml up node0 node1 node2 node3', shell=True, stdout=subprocess.PIPE)
    return proc

def run_nodes_container(nodes):
    proc = subprocess.Popen('docker-compose -f ./docker-compose-py.yml scale nodes={}'.format(nodes), shell=True, stdout=subprocess.PIPE)
    return proc

def run_eval_container():
    proc = subprocess.Popen('docker run --gpus all --rm -it -v {}:/root/:z -v {}:/mountdata/ -n isl-bcfl_localnet tony92151/py-abci python3 /root/py-app/eval/eval.py -config /root/py-app/config/config.ini'.format(sys.abspath("./script"), sys.abspath("./data")), shell=True, stdout=subprocess.PIPE)
    return proc

def run_echo():
    proc = subprocess.Popen("echo asdasd $pwd", shell=True)
    return proc

def set_config_file(f):
    proc = subprocess.Popen("cp {} {}/config_run.ini".format(f, os.path.dirname(f)), shell=True)
    return proc

def stop_network_container():
    proc = subprocess.Popen('docker-compose -f ./docker-compose-py.yml stop ipfsA', shell=True, stdout=subprocess.PIPE)
    return proc

def terminate_all_container():
    proc = subprocess.Popen('docker-compose -f ./docker-compose-py.yml down -v', shell=True, stdout=subprocess.PIPE)
    return proc

def send_create_task_TX():
    proc = subprocess.Popen("echo asdasd $pwd", shell=True)
    return proc

def move_result_to_save_folder():
    # move config.ini
    # move 
    return proc

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help="path to config", type=str, default=None)
    parser.add_argument('--output', help="output", type=str, default=None)
    args = parser.parse_args()

    if args.config is None or args.output is None:
        print("Please set --config & --output.")
        exit()

    con_path = os.path.abspath(args.config)
    print("Read config: {}".format(con_path))
    con = Configer(con_path)

    # set up config file
    p_config = set_config_file(con_path)

    # launch ipfs container
    p_ipfs = run_ipfs_container()
    print("PID : ipfs : {}".format(p_ipfs.pid))
    time.sleep(1)

    # launch network capture container
    p_net = run_network_container()
    print("PID : network : {}".format(p_net.pid))
    time.sleep(1)

    # launch network capture container
    p_vnodes = run_vlaidatror_nodes_container()
    print("PID : vlaidatror_nodes : {}".format(p_vnodes.pid))
    time.sleep(1)

    # launch scalble-nodes container
    if not con.bcfl.get_scale_nodes() == 0:
        print("Scale node : {}".format(con.bcfl.get_scale_nodes()))
        p_snodes = run_nodes_container(con.bcfl.get_scale_nodes())
        print("PID : scale_nodes : {}".format(p_snodes.pid))
        time.sleep(1)

    # time.sleep(30)
    # send create-task TX to strat trining.

    # check whether training process is finish

    # launch eval container
    #p_eval = run_eval_container()

    # move all result to save_path
    #p_save = move_result_to_save_folder()

    # terminate all container
    time.sleep(30)
    p_t = terminate_all_container()
    p_t.wait()
    print("Done\n")
