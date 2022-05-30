# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import dataclay_mds.grpc.protos.generated.metadata_service_pb2 as metadata__service__pb2


class MetadataServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.NewAccount = channel.unary_unary(
                '/dataclay_mds.grpc.protos.generated.MetadataService/NewAccount',
                request_serializer=metadata__service__pb2.NewAccountRequest.SerializeToString,
                response_deserializer=metadata__service__pb2.NewAccountResponse.FromString,
                )
        self.NewSession = channel.unary_unary(
                '/dataclay_mds.grpc.protos.generated.MetadataService/NewSession',
                request_serializer=metadata__service__pb2.NewSessionRequest.SerializeToString,
                response_deserializer=metadata__service__pb2.NewSessionResponse.FromString,
                )


class MetadataServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def NewAccount(self, request, context):
        """Account Manager
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def NewSession(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MetadataServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'NewAccount': grpc.unary_unary_rpc_method_handler(
                    servicer.NewAccount,
                    request_deserializer=metadata__service__pb2.NewAccountRequest.FromString,
                    response_serializer=metadata__service__pb2.NewAccountResponse.SerializeToString,
            ),
            'NewSession': grpc.unary_unary_rpc_method_handler(
                    servicer.NewSession,
                    request_deserializer=metadata__service__pb2.NewSessionRequest.FromString,
                    response_serializer=metadata__service__pb2.NewSessionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'dataclay_mds.grpc.protos.generated.MetadataService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class MetadataService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def NewAccount(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/dataclay_mds.grpc.protos.generated.MetadataService/NewAccount',
            metadata__service__pb2.NewAccountRequest.SerializeToString,
            metadata__service__pb2.NewAccountResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def NewSession(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/dataclay_mds.grpc.protos.generated.MetadataService/NewSession',
            metadata__service__pb2.NewSessionRequest.SerializeToString,
            metadata__service__pb2.NewSessionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
