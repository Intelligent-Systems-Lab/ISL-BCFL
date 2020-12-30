import torch
import torch.nn as nn
from torchvision import transforms
from torch.utils.data import DataLoader
from torch.utils.data.sampler import SubsetRandomSampler

import sys
sys.path.append('./proto')
import trainer_pb2
import trainer_pb2_grpc

from concurrent import futures
import logging
import grpc



class Aggregator(trainer_pb2_grpc.AggregatorServicer):
    def Aggregate(self, request, result):
        print(request.BaseModel)
        print("training")
        return trainer_pb2.TrainResult(Round=1, BaseModelResult="Done")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    trainer_pb2_grpc.add_AggregatorServicer_to_server(Aggregator(), server)

    server.add_insecure_port('localhost:62287')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
