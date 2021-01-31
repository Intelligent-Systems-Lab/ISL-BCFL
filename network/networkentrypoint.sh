apk add wireshark tshark
chgrp wireshark /usr/bin/dumpcap

DATE=$(date "+%H_%M_%S")
FILE=/root/network_$DATE.pcap
touch $FILE
echo "Capture file : $FILE"
tshark -i bcfl -w $FILE
