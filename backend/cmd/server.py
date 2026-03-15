"""Start the gRPC server and the FastAPI/GraphQL gateway in one process.

Usage:
    python -m cmd.server [--db ./data/transit.db] [--grpc-port 50051] [--http-port 8080]
"""
from __future__ import annotations

import sys
import threading
from concurrent import futures
from pathlib import Path

import click
import grpc
import uvicorn

sys.path.insert(0, str(Path(__file__).parent.parent))

from gen.transit.v1 import transit_pb2_grpc
from internal.transit.service import TransitServicer
from internal.gateway.app import create_app


def _start_grpc_server(db_path: str, grpc_port: int) -> grpc.Server:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    transit_pb2_grpc.add_TransitServiceServicer_to_server(
        TransitServicer(db_path), server
    )
    server.add_insecure_port(f"[::]:{grpc_port}")
    server.start()
    return server


@click.command()
@click.option("--db", default="data/transit.db", show_default=True,
              help="Path to the SQLite database")
@click.option("--grpc-port", default=50051, show_default=True,
              help="gRPC server port")
@click.option("--http-port", default=8080, show_default=True,
              help="HTTP/GraphQL server port")
def main(db: str, grpc_port: int, http_port: int) -> None:
    db_path = Path(db)
    if not db_path.exists():
        click.echo(
            f"Warning: database '{db_path}' does not exist. "
            "Run 'python -m cmd.importer' first.",
            err=True,
        )

    click.echo(f"Starting gRPC server on port {grpc_port}...")
    grpc_server = _start_grpc_server(str(db_path), grpc_port)

    grpc_channel = grpc.insecure_channel(f"localhost:{grpc_port}")
    app = create_app(grpc_channel)

    click.echo(f"Starting HTTP/GraphQL gateway on port {http_port}...")
    click.echo(f"  GraphiQL playground: http://localhost:{http_port}/graphql")

    try:
        uvicorn.run(app, host="0.0.0.0", port=http_port, log_level="info")
    finally:
        grpc_server.stop(grace=5)
        grpc_channel.close()


if __name__ == "__main__":
    main()
