
import socket
import struct
import time
import json
import sys
from signal import signal, SIGINT


def get_mac_addr(bytes_data):
    bytes_str = map('{:02X}'.format, bytes_data)
    return ':'.join(bytes_str)

def ehternet_frame(data):
    dest_mac, src_mac, proto = struct.unpack('! 6s 6s H', data[:14])
    return get_mac_addr(dest_mac), get_mac_addr(src_mac), socket.htons(proto), data[14:]

def store(data, path="/root/",pak=0):
    print("Save data to {}".format(path+'traffic_data_'+str(pak)+'.json'))
    with open(path+'/traffic_data_'+str(pak)+'.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)

def handler(signal_received, frame):
    print('SIGINT or CTRL-C detected. Exiting...')
    exit(0)



if __name__ == '__main__':
    signal(SIGINT, handler)
    mydict = {"Time":[],"Destination":[],"Source":[],"Payload":[]}
    conn = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    pakage=0
    count=1
    pa = sys.argv[1]
    while True:
        if count%10 == 0:
            print("Network traffic capturing...")
        if count%100 == 0:
            store(data=mydict, path=pa, pak=pakage)
            pakage+=1
            mydict['Time']=[]
            mydict['Destination']=[]
            mydict['Source']=[]
            mydict['Payload']=[]

        raw_data, data = conn.recvfrom(65536)
        dest_mac, src_mac, eth_proto, data = ehternet_frame(raw_data)        

        mydict['Time'].append(time.strftime("%H:%M:%S", time.localtime()))
        mydict['Destination'].append(dest_mac)
        mydict['Source'].append(src_mac)
        mydict['Payload'].append(len(data))
        count += 1
        #print('\nEthernet Frame: ')
        #print('Destination: {}, Source: {}, Protocol: {}'.format(dest_mac, src_mac, eth_proto))
        


