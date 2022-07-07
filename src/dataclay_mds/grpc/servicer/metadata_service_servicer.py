import logging
import traceback

import grpc
from google.protobuf.empty_pb2 import Empty

from dataclay_common.protos import metadata_service_pb2_grpc
from dataclay_common.protos import metadata_service_pb2
from dataclay_common.protos import common_messages_pb2

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
                request.password)
        except Exception as ex:
            msg = str(ex)
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            traceback.print_exc()
            return Empty()
        return Empty()

    def NewSession(self, request, context):
        try:
            result = self.metadata_service.new_session(
                request.username,
                request.password,
                request.default_dataset)
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
                request.dataset)
        except Exception as ex:
            msg = str(ex)
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            traceback.print_exc()
            return Empty()
        return Empty()

    def CloseSession(self, request, context):
        try:
            result = self.metadata_service.close_session(request.id)
        except Exception as ex:
            msg = str(ex)
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            traceback.print_exc()
            return Empty()
        return Empty()

    def GetDataclayID(self, request, context):
        try:
            result = self.metadata_service.get_dataclay_id()
        except Exception as ex:
            msg = str(ex)
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            traceback.print_exc()
            return metadata_service_pb2.GetDataclayIDResponse()
        return metadata_service_pb2.GetDataclayIDResponse(dataclay_id=str(result))

    def GetAllExecutionEnvironments(self, request, context):
        try:
            result = self.metadata_service.get_all_execution_environments()
            response = dict()
            for id, exe_env in result.items():
                response[id] = exe_env.get_proto()
        except Exception as ex:
            msg = str(ex)
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            traceback.print_exc()
            return metadata_service_pb2.GetAllExecutionEnvironmentsResponse()
        return metadata_service_pb2.GetAllExecutionEnvironmentsResponse(exe_envs=response)

    def AutoregisterEE(self, request, context):
        try:
            self.metadata_service.autoregister_ee(
                request.id,
                request.name,
                request.hostname,
                request.port,
                request.lang)
        except Exception as ex:
            msg = str(ex)
            context.set_details(msg)
            context.set_code(grpc.StatusCode.INTERNAL)
            traceback.print_exc()
            return Empty()
        return Empty()
