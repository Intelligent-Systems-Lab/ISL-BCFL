

build_proto:
	cd ./proto
	protoc --go_out=plugins=grpc:. *.proto

build:
	go build -o trainer main.go ./proto/trniner.pb.go