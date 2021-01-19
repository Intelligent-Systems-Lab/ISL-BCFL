echo "Setting up trainer node..."

PORT=62281

STATIC_IP=$(hostname -I)
STATIC_IP=${STATIC_IP% }

if [ -z "$DATASET" ]
then
    DATASET=mnist
fi

# echo "STATIC_IP = $STATIC_IP"

cd

python3 -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. proto/trainer.proto

echo "Start trainer node at port ... $STATIC_IP:$PORT with "$DATASET"_train_$ID.csv"
DATAPATH=/mountdata/$DATASET/"$DATASET"_train_$ID.csv

python3 -u trainer.py --data $DATAPATH --port $PORT --device GPU --batch 256