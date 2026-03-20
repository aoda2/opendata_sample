"""FastAPI application wiring together the GraphQL gateway and CORS."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from internal.gateway.schema import schema


def create_app(grpc_channel) -> FastAPI:
    app = FastAPI(title="Yokohama Transit GraphQL Gateway")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    async def get_context(request: Request):
        return {"grpc_channel": grpc_channel, "request": request}

    graphql_router = GraphQLRouter(
        schema,
        context_getter=get_context,
        graphql_ide="graphiql",
    )
    app.include_router(graphql_router, prefix="/graphql")

    return app
