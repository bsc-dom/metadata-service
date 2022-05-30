#!/bin/bash
PATH_PROTOS=src/dataclay_mds/grpc/protos

python3 -m grpc_tools.protoc -I$PATH_PROTOS --python_out=$PATH_PROTOS/generated --grpc_python_out=$PATH_PROTOS/generated $PATH_PROTOS/metadata_service.proto

# Replace import path
sed -i '0,/metadata_service_pb2/{s/metadata_service_pb2/dataclay_mds.grpc.protos.generated.metadata_service_pb2/}' $PATH_PROTOS/generated/metadata_service_pb2_grpc.py