
instll_dep:
	go install google.golang.org/protobuf/cmd/protoc-gen-go
	python -m pip install grpcio

.ONESHELL:
build_proto:
	#protoc -I=. --python_out=. --grpc_python_out=. proto/trainer.proto
	#python3 -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. proto/trainer.proto
	#protoc -I=${GOPATH}/src/github.com/ --go_out=. proto/trainer.proto
	#
	protoc --go-grpc_out=:./proto --go_out=:./proto proto/trainer.proto
	# mv BCFL ${GOPATH}/src/github.com
	# cd ${GOPATH}/src/github.com/BCFL/trainer
	# go mod init github.com/BCFL/trainer
	# go build github.com/BCFL/trainer
	# go install

build:
	go build -o trainer main.go ./proto/trainer.pb.go

clean:
	rm -r ${GOPATH}/src/github.com/BCFL