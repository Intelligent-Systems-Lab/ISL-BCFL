import sys
from scapy.utils import RawPcapReader
import matplotlib.pyplot as plt

# file_name = "/Users/tonyguo/Desktop/test4.pcap"
# file_name = sys.argv[1]


def analysis_pcap(file_name):
    pcap = RawPcapReader(file_name)
    packet_pcap = pcap.read_all()
    pkt_data = []

    time_start = (packet_pcap[0][1].tshigh << 32) | packet_pcap[0][1].tslow
    time_record = [time_start]
    flow =  [packet_pcap[0][1].wirelen]
    flows = [packet_pcap[0][1].wirelen]
    sum_value = packet_pcap[0][1].wirelen
    for i in packet_pcap[1:]:
        pkt_data.append(i[0])
        flow.append(i[1].wirelen)
        sum_value += i[1].wirelen
        flows.append(sum_value)
        time_record.append((i[1].tshigh << 32) | i[1].tslow)
    
    time_record = [(t - time_start)/10 ** 4 for t in time_record]
    print("capture {} packets, {} bytes, {} mb".format(len(packet_pcap), flows[-1], flows[-1] / 10 ** 6))
    pkt_data = pkt_data[:-5]
    time_record = time_record[:-5]
    flow = flow[:-5]
    flows = flows[:-5]

    return pkt_data, time_record, flow, flows


def plt_save(data, time_, save_file):
    plt.title("traffic(MB)-time(ms)")
    plt.grid(True)
    plt.ylabel("MB")
    plt.xlabel("Time(ms)")
    plt.plot(data, time_, color='red')
    plt.savefig(save_file)


if __name__ == "__main__":
    _, time_record, flow, flows = analysis_pcap(sys.argv[1])
    # print(time_record)
    # print(max(time_record), max(flow))
    #print(flows)
    flows = [i/10**6 for i in flows]
    plt_save(time_record, flows, sys.argv[2])
    plt_save(time_record, flow, sys.argv[3])
