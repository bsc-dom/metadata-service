from concurrent import futures
import logging

import grpc

from dataclay_common.protos import metadata_service_pb2_grpc
from dataclay_mds.grpc.servicer.metadata_service_servicer import MetadataServiceServicer
from dataclay_mds.conf import settings
from dataclay_mds.metadata_service import MetadataService

logger = logging.getLogger(__name__)


class MetadataServiceSrv:
    def __init__(self):
        self.metadata_service = None
        self.grpc_server = None
        pass

    def start(self):
        # TODO: Get environment variable for global settings
        self.metadata_service = MetadataService()
        self.start_grpc_server()

    def start_grpc_server(self):
        self.grpc_server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=settings.THREAD_POOL_WORKERS)
        )
        metadata_service_pb2_grpc.add_MetadataServiceServicer_to_server(
            MetadataServiceServicer(self.metadata_service), self.grpc_server
        )

        address = f"{settings.SERVER_LISTEN_ADDR}:{settings.SERVER_LISTEN_PORT}"
        self.grpc_server.add_insecure_port(address)
        self.grpc_server.start()
        self.grpc_server.wait_for_termination()
