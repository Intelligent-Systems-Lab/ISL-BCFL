apt-get update && apt-get -y upgrade

apt-get install -y python3-pip

pip3 install -r requirements.txt

go install google.golang.org/grpc/cmd/protoc-gen-go-grpc