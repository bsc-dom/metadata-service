import logging
import traceback

from dataclay_mds.grpc.protos.generated import metadata_service_pb2_grpc
from dataclay_mds.grpc.protos.generated import metadata_service_pb2

logger = logging.getLogger(__name__)

class MetadataServiceServicer(metadata_service_pb2_grpc.MetadataServiceServicer):
    """"Provides methods that implement functionality of metadata server"""
    
    def __init__(self, metadata_service):
        self.metadata_service = metadata_service
        logger.debug('Initialized MetadataServiceServicer')

    # TODO: define get_exception_info(..) to serialize excpetions

    def NewAccount(self, request, context):
        try:
            result = self.metadata_service.new_account(request.username, request.password)
        except Exception as ex:
            traceback.print_exc()
            return self.get_exception_info(ex)
        return metadata_service_pb2.NewAccountResponse(username=result)

    def NewSession(self, request, context):
        try:
            result = self.metadata_service.new_session(request.username, request.password)
        except Exception as ex:
            traceback.print_exc()
            return self.get_exception_info(ex)
        return metadata_service_pb2.NewSessionResponse(id=result)
