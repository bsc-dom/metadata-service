import logging
import atexit

import grpc

from dataclay_mds.protos import metadata_service_pb2_grpc
from dataclay_mds.protos import metadata_service_pb2

logger = logging.getLogger(__name__)

class MDSClient:
    def __init__(self, hostname, port):
        self.address = f'{hostname}:{port}'
        self.channel = grpc.insecure_channel(self.address)
        self.stub = metadata_service_pb2_grpc.MetadataServiceStub(self.channel)
        atexit.register(self.close)

    def close(self):
        self.channel.close()

    def new_account(self, username, password):
        request = metadata_service_pb2.NewAccountRequest(
            username=username, 
            password=password
        )
        return self.stub.NewAccount(request)

    def new_session(self, username, password, default_dataset):
        request = metadata_service_pb2.NewSessionRequest(
            username=username,
            password=password,
            default_dataset=default_dataset
        )
        return self.stub.NewSession(request)

    def new_dataset(self, username, password, dataset):
        request = metadata_service_pb2.NewDatasetRequest(
            username=username,
            password=password,
            dataset=dataset
        )
        return self.stub.NewDataset(request)
