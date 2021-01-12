echo "Setting up trainer node..."

PORT=62281

STATIC_IP=$(hostname -I)
STATIC_IP=${STATIC_IP% }

# echo "STATIC_IP = $STATIC_IP"

cd

python3 -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. proto/trainer.proto

echo "Start trainer node at port ... $STATIC_IP:$PORT with mnist_train_$ID.csv"
python3 -u trainer.py --data /mountdata/mnist/mnist_train_$ID.csv --port $PORT # >> /root/log/log.log 2>&1 &