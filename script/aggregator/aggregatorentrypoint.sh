echo "Setting up aggregator node..."

PORT=62287

cd

python3 -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. proto/aggregator.proto

echo "Start aggregator node at port ... $PORT"
python3 aggregator.py --port $PORT
# python3 aggregator.py --port $PORT >> /root/log/log.log 2>&1 & | tee