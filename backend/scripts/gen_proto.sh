#!/usr/bin/env bash
# Generate Python gRPC code from proto definitions.
# Run from the backend/ directory: bash scripts/gen_proto.sh
set -euo pipefail

cd "$(dirname "$0")/.."

python -m grpc_tools.protoc \
  -I proto \
  --python_out=gen \
  --grpc_python_out=gen \
  proto/transit/v1/transit.proto

# Fix import path: protoc generates `from transit.v1 import ...` but we need `from gen.transit.v1 import ...`
sed -i '' 's/^from transit\.v1 import/from gen.transit.v1 import/' gen/transit/v1/transit_pb2_grpc.py 2>/dev/null || \
sed -i    's/^from transit\.v1 import/from gen.transit.v1 import/' gen/transit/v1/transit_pb2_grpc.py

echo "Proto generation complete: gen/transit_pb2.py, gen/transit_pb2_grpc.py"
