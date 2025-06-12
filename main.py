import logging
from typing import Any
import dtlpy as dl
from pydantic_settings import BaseSettings, SettingsConfigDict
from mcp.server.fastmcp import FastMCP, Context
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from datetime import timedelta
import os
import jwt
import time
import requests
import traceback

logger = logging.getLogger("[DATALOOP-MCP]")

APP_ROUTE_URL = "https://gate.dataloop.ai/api/v1/apps/dataloop-mcp-684a6bafdc4346909fe2d7d2/panels/mcp/"
SERVER_URL = "https://dataloop-mcp-684a6bafdc4346909fe2d7d2.apps.dataloop.ai/mcp/"


class ServerSettings(BaseSettings):
    """Settings for the Dataloop MCP server."""

    model_config = SettingsConfigDict(env_prefix="MCP_DATALOOP_")
    server_url: str = SERVER_URL

    def __init__(self, **data):
        super().__init__(**data)


def is_expired(app_jwt: str) -> bool:
    """Check if the APP_JWT is expired."""
    try:
        decoded = jwt.decode(app_jwt, options={"verify_signature": False})
        if decoded.get("exp") < time.time():
            return True
        return False
    except jwt.ExpiredSignatureError:
        return True
    except Exception as e:
        logger.error(f"Error decoding JWT: {e}")
        return True


def get_app_jwt() -> str:
    """Get the APP_JWT from the request headers."""
    app_jwt = os.environ.get('APP_JWT', None)

    if app_jwt is None or is_expired(app_jwt):
        dl.client_api.token = os.environ.get('DATALOOP_API_KEY')
        session = requests.Session()
        response = session.get(APP_ROUTE_URL, headers=dl.client_api.auth)
        # The JWT is likely in the cookies after redirects
        app_jwt = session.cookies.get("JWT-APP")
    if not app_jwt:
        raise ValueError(
            "APP_JWT is missing. Please set the APP_JWT environment variable or ensure authentication is working."
        )
    os.environ['APP_JWT'] = app_jwt
    return app_jwt


def create_dataloop_mcp_server(settings: ServerSettings) -> FastMCP:
    """Create a FastMCP server for Dataloop with Bearer token authentication."""

    app = FastMCP(
        name="Dataloop MCP Server",
        instructions="A multi-tenant MCP server for Dataloop with authentication",
        stateless_http=True,
        debug=True,
    )

    @app.tool(description="Ask the Dataloop docs")
    async def ask_dataloop(question: str, ctx: Context) -> dict[str, Any]:
        """Ask the Dataloop documentation.
        Args:
            question: The question to ask
        """
        try:
            app_jwt = get_app_jwt()
            server_url = settings.server_url
            # Create a session using the client streams
            async with streamablehttp_client(server_url, headers={"Cookie": f"JWT-APP={app_jwt}"}) as (read, write, _):
                async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=60)) as session:
                    # Initialize the connection
                    await session.initialize()
                    # Call a tool
                    tool_result = await session.call_tool("ask_dataloop", {"question": question})
                    return tool_result
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": f"Failed to process request: {str(e)}"}

    return app


def main() -> int:
    logger.info("Starting Dataloop MCP server in stdio mode")

    try:
        settings = ServerSettings()
        logger.info("Successfully configured Dataloop MCP server")

    except Exception as e:
        logger.error(f"Unexpected error during startup:\n{traceback.format_exc()}")
        return 1

    try:
        mcp_server = create_dataloop_mcp_server(settings)
        logger.info("Starting Dataloop MCP server in stdio mode")
        logger.info("Users should provide their API key in the Authorization header as a Bearer token")
        mcp_server.run(transport="stdio")
        return 0
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        return 1


if __name__ == "__main__":
    main()
