import logging
import traceback

import grpc

from dataclay_common.protos import metadata_service_pb2_grpc
from dataclay_common.protos import metadata_service_pb2

logger = logging.getLogger(__name__)

class MetadataServiceServicer(metadata_service_pb2_grpc.MetadataServiceServicer):
    """"Provides methods that implement functionality of metadata server"""
    
    def __init__(self, metadata_service):
        self.metadata_service = metadata_service
        logger.debug('Initialized MetadataServiceServicer')

    # TODO: define get_exception_info(..) to serialize excpetions

    def NewAccount(self, request, context):
        try:
            result = self.metadata_service.new_account(
                request.username, 
                request.password
            )
        except Exception as ex:
            msg = str(ex)
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            traceback.print_exc()
            return metadata_service_pb2.NewAccountResponse()
        return metadata_service_pb2.NewAccountResponse(username=result)

    def NewSession(self, request, context):
        try:
            result = self.metadata_service.new_session(
                request.username, 
                request.password,
                request.default_dataset
            )
        except Exception as ex:
            msg = str(ex)
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            traceback.print_exc()
            return metadata_service_pb2.NewSessionResponse()
        return metadata_service_pb2.NewSessionResponse(id=result)

    def NewDataset(self, request, context):
        try:
            result = self.metadata_service.new_dataset(
                request.username, 
                request.password,
                request.dataset
            )
        except Exception as ex:
            msg = str(ex)
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            traceback.print_exc()
            return metadata_service_pb2.NewDatasetResponse()
        return metadata_service_pb2.NewDatasetResponse()
