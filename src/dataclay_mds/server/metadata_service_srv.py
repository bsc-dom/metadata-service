
from concurrent import futures
import logging

import grpc

from dataclay_mds.grpc.generated import metadata_service_pb2_grpc
from dataclay_mds.grpc.servicer.metadata_service_servicer import MetadataServiceServicer
from dataclay_mds.conf import settings
from dataclay_mds.metadata_service import MetadataService 

logger = logging.getLogger(__name__)

class MetadataServiceSrv:

    def __init__(self):
        self.metadata_service = None
        pass

    def start(self):


        # TODO: Get environment variable for global settings

        self.metadata_service = MetadataService()
        metadata_service_servicer = MetadataServiceServicer(self.metadata_service)

        # Initialize and start grpc
        # TODO: Set max_workers from a configuration
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=settings.THREAD_POOL_WORKERS))
        metadata_service_pb2_grpc.add_MetadataServiceServicer_to_server(metadata_service_servicer, self.server)

        address = f'{settings.SERVER_LISTEN_ADDR}:{settings.SERVER_LISTEN_PORT}' 
        self.server.add_insecure_port(address)
        self.server.start()
        self.server.wait_for_termination()