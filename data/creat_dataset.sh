
#https://scidm.nchc.org.tw/dataset/mnist

NUMOFDATA=5

mkdir mnist
cd mnist
wget https://scidm.nchc.org.tw/dataset/mnist/resource/ce2b188c-bb3e-41ab-8dfc-d9b6e665fbd4/nchcproxy -O mnist-in-csv.zip
unzip mnist-in-csv.zip

cd ..
python3 mnist.py --data $(pwd)/mnist --n $NUMOFDATA
