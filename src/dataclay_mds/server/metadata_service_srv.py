import logging
import uuid
from concurrent import futures

import grpc
from dataclay_common.protos import metadata_service_pb2_grpc
from dataclay_common.metadata_service import MetadataService

from dataclay_mds.conf import settings
from dataclay_mds.grpc.servicer.metadata_service_servicer import MetadataServiceServicer

logger = logging.getLogger(__name__)


class MetadataServiceSrv:
    def __init__(self):
        self.metadata_service = None
        self.grpc_server = None
        pass

    def start(self):
        # TODO: Get environment variable for global settings
        self.metadata_service = MetadataService(settings.ETCD_HOST, settings.ETCD_PORT)
        dataclay_id = str(uuid.uuid4())
        self.metadata_service.autoregister_mds(
            dataclay_id,
            settings.METADATA_SERVICE_HOST,
            settings.METADATA_SERVICE_PORT,
            is_this=True,
        )
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
