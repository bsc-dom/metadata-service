import logging
import atexit

import grpc

from dataclay_mds.grpc.generated import metadata_service_pb2_grpc
from dataclay_mds.grpc.generated import metadata_service_pb2

logger = logging.getLogger(__name__)

# TODO: Use configparse to read connection details from config file
HOSTNAME = 'localhost'
PORT = 16587

class MDSClient:
    def __init__(self, hostname, port):
        self.address = f'{hostname}:{port}'
        self.channel = grpc.insecure_channel(self.address)
        self.stub = metadata_service_pb2_grpc.MetadataServiceStub(self.channel)
        atexit.register(self.close)

    def close(self):
        self.channel.close()

    def new_account(self, username, password):
        request = metadata_service_pb2.NewAccountRequest(username=username, password=password)
        response = self.stub.NewAccount(request)
        return response

def new_account(username, password):
    logger.info(f'Creating "{username}" account')

    mds_client = MDSClient(HOSTNAME, PORT)
    response = mds_client.new_account(username, password)

    logger.debug(f'Created account ({username}). Response -> {response}')


def get_backends(username, password):
    print(username, password)