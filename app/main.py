"""Compose and expose the FastMCP ASGI application.

Import and register new tools/resources here. Custom HTTP routes live in
``twynity.py`` and are separate from FastMCP's MCP transport.
"""

from contextlib import asynccontextmanager

from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.auth import get_auth_provider
from app.config import settings
from app.tools.notes import register_tool as register_notes
from app.twynity import register_routes
from app.ui.notes.resource import register_resource as register_notes_resource


@asynccontextmanager
async def app_lifespan(server):
    yield


mcp = FastMCP(
    settings.APP_TITLE,
    auth=get_auth_provider(),
    lifespan=app_lifespan,
)

register_notes(mcp)
register_notes_resource(mcp)
register_routes(mcp)

match settings.ENVIRONMENT:
    case "production":
        origins = ["https://tinytim.example.com"]
    case _:
        origins = ["*"]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["mcp-session-id"],
    )
]

app = mcp.http_app(middleware=middleware)


def create_app():
    """Create the ASGI application — useful for test clients and Docker."""
    return app


if __name__ == "__main__":
    import uvicorn

    port = settings.PORT
    uvicorn.run(app, host="0.0.0.0", port=port)
